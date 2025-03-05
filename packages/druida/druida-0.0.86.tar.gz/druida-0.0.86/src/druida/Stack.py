import sys  

from .DataManager import datamanager

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from torchvision.models import resnet18, resnet50, ResNet50_Weights, resnet152
import torchvision

sys.path.insert(0, '../druida_V01/src/')

import os
import copy

from tqdm import tqdm
from torch import optim
import logging 


from torch.utils.tensorboard import SummaryWriter

from .tools import toolkit
from .tools import utils

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO, datefmt="%I:%M:%S")

#Used to implement any prediction process
class Predictor:
    def __init__(self):
        
        self.checkDevice()

    def generate_VAE(self,mean, var, model):
        z_sample = torch.tensor([[mean, var]], dtype=torch.float).to(self.device)
        x_decoded = model.decode(z_sample)
        #image = x_decoded.detach().cpu().reshape(64, 64,3) # reshape vector to 2d array
        
        return x_decoded


    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )

# All training modules for the different algorithms used
class Trainer:
    

    def __init__(self, args):

        self.run_name = args.run_name
        self.learning_rate = args.learning_rate
        self.batch_size = args.batch_size
        self.epochs = args.epochs
        self.workers = args.workers
        self.gpu_number=args.gpu_number

        self.device=self.checkDevice()
        
    def training(self, trainFunction,testFunction, train_dataloader, test_dataloader, model, loss_fn, optimizer):
        acc=0
        acc_test=0
        loss=0
        test_loss=0
        loss_values = []
        test_loss_values = []
        train_acc_hist = []
        test_acc = []

        for t in range(self.epochs):
            dataiter = iter(train_dataloader)
            testdataiter = iter(test_dataloader)


            print(f"Epoch {t+1}\n-------------------------------")
            acc,loss=trainFunction(next(dataiter), model, loss_fn, optimizer, t,acc,loss)
            acc_test,test_loss=testFunction(next(testdataiter), model, loss_fn,len(train_dataloader), t, acc_test,test_loss)

            loss_values.append(loss)
            test_loss_values.append(test_loss)
            train_acc_hist.append(acc)
            test_acc.append(acc_test)
        print("Done!")

        return loss_values,test_loss_values,train_acc_hist, test_acc

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )


    def multiGPU(self, network):
        print('available Device:'+network.device)
        if (network.device == 'cuda' and (self.gpu_number > 1)):
            network=nn.DataParallel(network,list(range(self.gpu_number)))

        return network
    

    #Traininga  VAE
    def train_VAE(self,args):
        
        utils.setup_logging(self.run_name)

        model = toolkit.VAE().to(self.device)
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)   
        dataloader = utils.get_data_denormalize(args.image_size, args.dataset_path,self.batch_size)
        trainingLoss=[]

        logging.info(f"Starting epoch {self.epochs}:")
        
        pbar = tqdm(dataloader)
        model.train()

        for epoch in range(self.epochs):
            overall_loss = 0

            for batch_idx, (x, _) in enumerate(pbar):
                images=x.to(self.device)
                images = (images.clamp(-1, 1) + 1) / 2 #make all values between 0 and 1 
                #images = (x * 255).type(torch.uint8) #valid pixel range
                #images=images.reshape(self.batch_size,-1).to(self.device)
                images = images.view(images.size()[0], (64*64*3)).to(self.device)
                optimizer.zero_grad()

                x_hat, mean, log_var = model(images)
                loss = self.loss_function(images, x_hat, mean, log_var)
                
                overall_loss += loss.item()
                
                loss.backward()
                optimizer.step()
            
            trainingLoss.append(overall_loss)


            print("\tEpoch", epoch + 1, "\tAverage Loss: ", overall_loss/(batch_idx*self.batch_size))
        return trainingLoss,overall_loss, model


    def loss_function(self,x, x_hat, mean, log_var):
     
        reproduction_loss = nn.functional.binary_cross_entropy(x_hat, x, reduction='sum')

        KLD = - 0.5 * torch.sum(1+ log_var - mean.pow(2) - log_var.exp())

        return reproduction_loss + KLD
    

    #N Training an unconditional diffusion model

    def train_DM(self,args):

        utils.setup_logging(self.run_name)

        device = self.device

        dataloader = utils.get_data(args.image_size, args.dataset_path,self.batch_size)

        model = toolkit.UNet(device=self.device,c_in=3, c_out=3, time_dim=256).to(device)

        optimizer = optim.AdamW(model.parameters(), lr=self.learning_rate)

        mse = nn.MSELoss()

        diffusion = Diffusion(img_size=args.image_size, device=device,noise_steps=1000, beta_start=1e-4, beta_end=0.02)

        logger = SummaryWriter(os.path.join("runs", self.run_name))

        l = len(dataloader)

        """this corresponds to algorithm 1 """

        for epoch in range(self.epochs):

            logging.info(f"Starting epoch {epoch}:")

            pbar = tqdm(dataloader)

            for i, (images, _) in enumerate(pbar):
                images = images.to(device)

                t = diffusion.sample_timesteps(images.shape[0]).to(device)

                x_t, noise = diffusion.noise_images(images, t)

                predicted_noise = model(x_t, t)

                loss = mse(noise, predicted_noise)

                optimizer.zero_grad()

                loss.backward()

                optimizer.step()

                pbar.set_postfix(MSE=loss.item())

                logger.add_scalar("MSE", loss.item(), global_step=epoch * l + i)

            sampled_images = diffusion.sample(model, n=images.shape[0])

            utils.save_images(sampled_images, os.path.join("results", self.run_name, f"{epoch}.jpg"))
            torch.save(model.state_dict(), os.path.join("models", self.run_name, f"ckpt.pt"))


    def train_CDM(self,args):

        utils.setup_logging(self.run_name)

        device = self.device
        dataloader = utils.get_data(args.image_size, args.dataset_path,self.batch_size)
        model = toolkit.UNet_conditional(device=self.device,channel_in=3, channel_out=3, time_dim=256,num_classes=args.num_classes).to(device)
        
        optimizer = optim.AdamW(model.parameters(), lr=self.learning_rate)

        mse = nn.MSELoss()

        diffusion = Diffusion(img_size=args.image_size, device=device)
        logger = SummaryWriter(os.path.join("runs", self.run_name))
        l = len(dataloader)

        #Exponential Moving Average
        #We make a copy of the model in order to have a 
        #version in which we use EMA and one without it.

        ema = toolkit.EMA(0.995)

        ema_model = copy.deepcopy(model).eval().requires_grad_(False)

        for epoch in range(self.epochs):

            logging.info(f"Starting epoch {epoch}:")
            pbar = tqdm(dataloader)

            for i, (images, labels) in enumerate(pbar):

                images = images.to(device)
                labels = labels.to(device)


                t = diffusion.sample_timesteps(images.shape[0]).to(device)#Sampling time steps
                x_t, noise = diffusion.noise_images(images, t) #add noise

                #This is for the model to train 10% of the time with no labels
                #Classifier free diffusion guidance
                #Si no hay labels se entrena el clasificador sin condición
                if np.random.random() < 0.1:
                    labels = None


                predicted_noise = model(x_t, t, labels)
                #recibe imagenes con ruido, pasos de tiempo y labels
                loss = mse(noise, predicted_noise)

                optimizer.zero_grad()
                loss.backward()

                optimizer.step()

                #Apply Ema to model

                ema.step_ema(ema_model, model)

                pbar.set_postfix(MSE=loss.item())

                logger.add_scalar("MSE", loss.item(), global_step=epoch * l + i)

            if epoch % 10 == 0:

                labels = torch.arange(args.num_classes).long().to(device)
                print(labels)
                print(len(labels))

                sampled_images = diffusion.sample_cdm(model, n=len(labels), labels=labels)
                ema_sampled_images = diffusion.sample_cdm(ema_model, n=len(labels), labels=labels)
                utils.plot_images(sampled_images)
                utils.save_images(sampled_images, os.path.join("results", self.run_name, f"{epoch}.jpg"))
                utils.save_images(ema_sampled_images, os.path.join("results", self.run_name, f"{epoch}_ema.jpg"))
                torch.save(model.state_dict(), os.path.join("models", self.run_name, f"ckpt.pt"))
                torch.save(ema_model.state_dict(), os.path.join("models", self.run_name, f"ema_ckpt.pt"))
                torch.save(optimizer.state_dict(), os.path.join("models", self.run_name, f"optim.pt"))





#Build a DNN stack 
    
class DNN(nn.Module):

    def __init__(self, layers):
        super(DNN,self).__init__()

        self.checkDevice()
        self.layers = layers
        self.architecture=nn.Sequential()

        for layer in layers:
            self.architecture.add_module(layer['name'],layer['layer'])

        

    def push(self, layer):
        self.layers.append(layer) #each layer must come as dictionary with nn type
        return self.layers
 
    def drop_last(self):
        self.layers.pop() #each layer must come as dictionary with nn type
        return self.layers

    def clear(self):
        self.layers.clear() #each layer must come as dictionary with nn type
        return self.layers
    
    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    
    def forward(self, input):

        #{"name":"hidden1","layer":nn.Linear(8,120), "type":"hidden", "index",0}
        self.output =  input
        for layer in self.layers:
            action=layer['layer']
            self.output = action(self.output)
                
                
        return self.output
    


#Build a Generator for GAN stack 

class Generator(nn.Module):
    def __init__(self, ngpu, input_size, mapping_size, channels, leakyRelu_flag ):
        super(Generator, self).__init__()
        

        self.checkDevice()

        self.ngpu = ngpu            

        self.conv1 = nn.ConvTranspose2d(input_size, mapping_size * 8, 6, 1, 0, bias=False)
        self.conv2 = nn.BatchNorm2d(num_features=mapping_size * 8)
        if leakyRelu_flag:
            self.conv3 = nn.ReLU(True)
            self.conv6 = nn.ReLU(True)
            self.conv9 = nn.ReLU(True)
            self.conv12 = nn.ReLU(True)

        else:
            self.conv3 = nn.LeakyReLU(0.2)
            self.conv6 = nn.LeakyReLU(0.2)
            self.conv9 = nn.LeakyReLU(0.2)
            self.conv12 = nn.LeakyReLU(0.2)

        self.conv4 = nn.ConvTranspose2d(mapping_size * 8, mapping_size * 4, 6, 2, 2, bias=False)
        self.conv5 = nn.BatchNorm2d(mapping_size * 4)
        self.conv7 = nn.ConvTranspose2d(mapping_size * 4, mapping_size * 2, 6, 2, 4, bias=False)
        self.conv8 = nn.BatchNorm2d(mapping_size * 2)
        self.conv10 = nn.ConvTranspose2d(mapping_size * 2, mapping_size, 6, 2, 5, bias=False)
        self.conv11 = nn.BatchNorm2d(mapping_size)
        self.conv13 = nn.ConvTranspose2d(mapping_size, channels, 6, 2, 4, bias=False)
        self.conv14 = nn.Tanh()

    def forward(self, input):
        imageOut = input
        imageOut = self.conv1(imageOut)
        imageOut = self.conv2(imageOut)
        imageOut = self.conv3(imageOut)
        imageOut = self.conv4(imageOut)
        imageOut = self.conv5(imageOut)
        imageOut = self.conv6(imageOut)
        imageOut = self.conv7(imageOut)
        imageOut = self.conv8(imageOut)
        imageOut = self.conv9(imageOut)
        imageOut = self.conv10(imageOut)
        imageOut = self.conv11(imageOut)
        imageOut = self.conv12(imageOut)
        imageOut = self.conv13(imageOut)
        imageOut = self.conv14(imageOut)               
        return imageOut

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    

#Build a Discriminator for GAN stack 

class Discriminator(nn.Module):
    def __init__(self,label_length, ngpu=0, image_size=32, discriminator_mapping_size=0, channels=3):
        super(Discriminator, self).__init__()

        
        self.checkDevice()

        self.ngpu = ngpu            
        self.image_size = image_size
        self.channels = channels

        # Habitualmente en el primer ejerciio 
        # label_length era 800

        self.l1 = nn.Linear(label_length, image_size*image_size*channels, bias=False)            
        self.conv1 = nn.Conv2d(2*channels, discriminator_mapping_size, 6, 2, 4, bias=False) 
        self.conv2 = nn.LeakyReLU(0.2, inplace=True)
        self.conv3 = nn.Conv2d(discriminator_mapping_size, discriminator_mapping_size * 2, 6, 2, 5, bias=False)
        self.conv4 = nn.BatchNorm2d(discriminator_mapping_size * 2)
        self.conv5 = nn.LeakyReLU(0.2, inplace=True)
        self.conv6 = nn.Conv2d(discriminator_mapping_size * 2, discriminator_mapping_size * 4, 6, 2, 4, bias=False)
        self.conv7 = nn.BatchNorm2d(discriminator_mapping_size * 4)
        self.conv8 = nn.LeakyReLU(0.2, inplace=True)
        self.conv9 = nn.Conv2d(discriminator_mapping_size * 4, discriminator_mapping_size * 8, 6, 2, 2, bias=False)
        self.conv10 = nn.BatchNorm2d(discriminator_mapping_size * 8)
        self.conv11 = nn.LeakyReLU(0.2, inplace=True)
        self.conv12 = nn.Conv2d(discriminator_mapping_size * 8, 1, 6, 1, 0, bias=False)
        self.conv13 = nn.Sigmoid()


    def forward(self, input, label, b_size):
        x1 = input
        x2 = self.l1(label) #Size must be taken care = 800 in this case
        #the output is imagesize x imagesize x channel
        #hence the need of reshape 

        if self.ngpu == 0 :
        
            x2 = x2.reshape(int(b_size),self.channels,self.image_size,self.image_size) 
        else:
            x2 = x2.reshape(int(b_size/self.ngpu),self.channels,self.image_size,self.image_size) 

        combine = torch.cat((x1,x2),dim=1) # concatenate in a given dimension
        #esto viene del mismo paper sobre los CGAN

        combine = self.conv1(combine) #This conv1 considers 2 x channels from the combine
        combine = self.conv2(combine)
        combine = self.conv3(combine)
        combine = self.conv4(combine)
        combine = self.conv5(combine)
        combine = self.conv6(combine)
        combine = self.conv7(combine)
        combine = self.conv8(combine)
        combine = self.conv9(combine)
        combine = self.conv10(combine)
        combine = self.conv11(combine)
        combine = self.conv12(combine)
        combine = self.conv13(combine)
        return combine

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    

#Build a Diffusion  model pipeline

# 256
class Generator_V2(nn.Module):
    def __init__(self, imagesize, ngpu,spectra_input_size,latent_size, mapping_size,initial_depth, channels, leakyRelu_flag ):
        super(Generator_V2, self).__init__()
        

        self.checkDevice()
        self.spectra_len=spectra_input_size
        self.latent_len=latent_size
        self.ngpu = ngpu   
        self.imagesize = imagesize            
         
        # 512 canales de entrada
        self.depth=initial_depth#512
        self.l1 = nn.Linear(self.spectra_len, 4*4*self.depth, bias=False)            
        self.l2 = nn.Linear(self.latent_len, 4*4*self.depth, bias=False)            

        self.conv1 = nn.ConvTranspose2d(self.depth*2, mapping_size * 8, 5, 1, 0, bias=False)
        self.conv2 = nn.BatchNorm2d(num_features=mapping_size * 8)
        if leakyRelu_flag:
            self.conv3 = nn.ReLU(True)
            self.conv6 = nn.ReLU(True)
            self.conv9 = nn.ReLU(True)
            self.conv12 = nn.ReLU(True)

        else:
            self.conv3 = nn.LeakyReLU(0.2)
            self.conv6 = nn.LeakyReLU(0.2)
            self.conv9 = nn.LeakyReLU(0.2)
            self.conv12 = nn.LeakyReLU(0.2)

        self.conv4 = nn.ConvTranspose2d(mapping_size * 8, mapping_size * 4, 6, 2, 2, bias=False)
        self.conv5 = nn.BatchNorm2d(mapping_size * 4)

        self.conv7 = nn.ConvTranspose2d(mapping_size * 4, mapping_size * 2, 6, 2, 2, bias=False)
        self.conv8 = nn.BatchNorm2d(mapping_size * 2)

        self.conv10 = nn.ConvTranspose2d(mapping_size * 2, mapping_size, 6, 2, 2, bias=False)
        self.conv11 = nn.BatchNorm2d(mapping_size)

        if self.imagesize==128:
            self.conv13_1 = nn.ConvTranspose2d(mapping_size, 32, 6, 2, 2, bias=False)
            self.conv14_1 = nn.BatchNorm2d(32)
            self.conv15_1 = nn.LeakyReLU(0.2)

            self.conv13 = nn.ConvTranspose2d(32, channels, 5, 1, 2, bias=False)
        
        elif self.imagesize==256:
            self.conv13_1 = nn.ConvTranspose2d(mapping_size, 32, 6, 2, 2, bias=False)
            self.conv14_1 = nn.BatchNorm2d(32)
            self.conv15_1 = nn.LeakyReLU(0.2)

            self.conv13_2 = nn.ConvTranspose2d(32, 16, 6, 2, 2, bias=False)
            self.conv14_2 = nn.BatchNorm2d(16)
            self.conv15_2 = nn.LeakyReLU(0.2)

            

            self.conv13 = nn.ConvTranspose2d(16, channels, 5, 1, 2, bias=False)

        elif self.imagesize==512:
            self.conv13_1 = nn.ConvTranspose2d(mapping_size, 32, 6, 2, 2, bias=False)
            self.conv14_1 = nn.BatchNorm2d(32)
            self.conv15_1 = nn.LeakyReLU(0.2)

            self.conv13_2 = nn.ConvTranspose2d(32, 16, 6, 2, 2, bias=False)
            self.conv14_2 = nn.BatchNorm2d(16)
            self.conv15_2 = nn.LeakyReLU(0.2)

            self.conv13_3 = nn.ConvTranspose2d(16, 8, 6, 2, 2, bias=False)
            self.conv14_3 = nn.BatchNorm2d(8)
            self.conv15_3 = nn.LeakyReLU(0.2)

            self.conv13 = nn.ConvTranspose2d(8, channels, 5, 1, 2, bias=False)

        else:

            self.conv13 = nn.ConvTranspose2d(mapping_size, channels, 5, 1, 2, bias=False)


        self.conv14 = nn.Tanh()

    def forward(self, input, latent, b_size):

        x_condspectra = self.l1(input) #Size must be taken care = 800 in this case
        x_latent = self.l2(latent) #Size must be taken care = 800 in this case

        if self.ngpu == 0 :
        
            x_condspectra = x_condspectra.reshape(int(b_size),self.depth,4,4) 
            x_latent = x_latent.reshape(int(b_size),self.depth,4,4) 

        else:
            x_condspectra = x_condspectra.reshape(int(b_size/self.ngpu),self.depth,4,4) 
            x_latent = x_latent.reshape(int(b_size/self.ngpu),self.depth,4,4) 

        combine = torch.cat((x_latent,x_condspectra),dim=1) # concatenate in a given dimension
        #esto viene d

        imageOut = combine

        imageOut = self.conv1(imageOut)
        imageOut = self.conv2(imageOut)
        imageOut = self.conv3(imageOut)
        imageOut = self.conv4(imageOut)
        imageOut = self.conv5(imageOut)
        imageOut = self.conv6(imageOut)
        imageOut = self.conv7(imageOut)
        imageOut = self.conv8(imageOut)
        imageOut = self.conv9(imageOut)
        imageOut = self.conv10(imageOut)
        imageOut = self.conv11(imageOut)
        imageOut = self.conv12(imageOut)

        if self.imagesize==128:
            imageOut = self.conv13_1(imageOut)
            imageOut = self.conv14_1(imageOut)
            imageOut = self.conv15_1(imageOut)
            imageOut = self.conv13(imageOut)

        elif self.imagesize==256:
            imageOut = self.conv13_1(imageOut)
            imageOut = self.conv14_1(imageOut)
            imageOut = self.conv15_1(imageOut)

            imageOut = self.conv13_2(imageOut)
            imageOut = self.conv14_2(imageOut)
            imageOut = self.conv15_2(imageOut)



            imageOut = self.conv13(imageOut)

        elif self.imagesize==512:
            imageOut = self.conv13_1(imageOut)
            imageOut = self.conv14_1(imageOut)
            imageOut = self.conv15_1(imageOut)

            imageOut = self.conv13_2(imageOut)
            imageOut = self.conv14_2(imageOut)
            imageOut = self.conv15_2(imageOut)

            imageOut = self.conv13_3(imageOut)
            imageOut = self.conv14_3(imageOut)
            imageOut = self.conv15_3(imageOut)

            imageOut = self.conv13(imageOut)
        else:

            imageOut = self.conv13(imageOut)

        imageOut = self.conv14(imageOut)               
        return imageOut

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    
# GEnerator 3 goes directly to 128 shapes
class Generator_V3(nn.Module):
    def __init__(self, imagesize, ngpu,spectra_input_size,latent_size, mapping_size,initial_depth, channels, leakyRelu_flag ):
        super(Generator_V2, self).__init__()
        

        self.checkDevice()
        self.spectra_len=spectra_input_size
        self.latent_len=latent_size
        self.ngpu = ngpu   
        self.imagesize = imagesize            
         
        # 512 canales de entrada
        self.depth=initial_depth#512
        self.l1 = nn.Linear(self.spectra_len, 4*4*self.depth, bias=False)            
        self.l2 = nn.Linear(self.latent_len, 4*4*self.depth, bias=False)            

        self.conv1 = nn.ConvTranspose2d(self.depth*2, mapping_size * 8, 5, 1, 0, bias=False)
        self.conv2 = nn.BatchNorm2d(num_features=mapping_size * 8)
        if leakyRelu_flag:
            self.conv3 = nn.ReLU(True)
            self.conv6 = nn.ReLU(True)
            self.conv9 = nn.ReLU(True)
            self.conv12 = nn.ReLU(True)

        else:
            self.conv3 = nn.LeakyReLU(0.2)
            self.conv6 = nn.LeakyReLU(0.2)
            self.conv9 = nn.LeakyReLU(0.2)
            self.conv12 = nn.LeakyReLU(0.2)

        self.conv4 = nn.ConvTranspose2d(mapping_size * 8, mapping_size * 4, 6, 2, 2, bias=False)
        self.conv5 = nn.BatchNorm2d(mapping_size * 4)

        

        if self.imagesize==128:

            self.conv7 = nn.ConvTranspose2d(mapping_size * 4, mapping_size * 2, 6, 2, 2, bias=False)
            self.conv8 = nn.BatchNorm2d(mapping_size * 2)

            self.conv10 = nn.ConvTranspose2d(mapping_size * 2, mapping_size, 6, 2, 2, bias=False)
            self.conv11 = nn.BatchNorm2d(mapping_size)
            self.conv13_1 = nn.ConvTranspose2d(mapping_size, 32, 6, 2, 2, bias=False)
            self.conv14_1 = nn.BatchNorm2d(32)
            self.conv15_1 = nn.LeakyReLU(0.2)

            self.conv13 = nn.ConvTranspose2d(32, channels, 5, 1, 2, bias=False)

        else:
            # 64x64 images
            self.conv7 = nn.ConvTranspose2d(mapping_size * 4, mapping_size * 2, 6, 2, 2, bias=False)
            self.conv8 = nn.BatchNorm2d(mapping_size * 2)

            self.conv10 = nn.ConvTranspose2d(mapping_size * 2, mapping_size, 6, 2, 2, bias=False)
            self.conv11 = nn.BatchNorm2d(mapping_size)
            self.conv13 = nn.ConvTranspose2d(mapping_size, channels, 5, 1, 2, bias=False)


        self.conv14 = nn.Tanh()

    def forward(self, input, latent, b_size):

        x_condspectra = self.l1(input) #Size must be taken care = 800 in this case
        x_latent = self.l2(latent) #Size must be taken care = 800 in this case

        if self.ngpu == 0 :
        
            x_condspectra = x_condspectra.reshape(int(b_size),self.depth,4,4) 
            x_latent = x_latent.reshape(int(b_size),self.depth,4,4) 

        else:
            x_condspectra = x_condspectra.reshape(int(b_size/self.ngpu),self.depth,4,4) 
            x_latent = x_latent.reshape(int(b_size/self.ngpu),self.depth,4,4) 

        combine = torch.cat((x_latent,x_condspectra),dim=1) # concatenate in a given dimension
        #esto viene d

        imageOut = combine

        imageOut = self.conv1(imageOut)
        imageOut = self.conv2(imageOut)
        imageOut = self.conv3(imageOut)
        imageOut = self.conv4(imageOut)
        imageOut = self.conv5(imageOut)
        imageOut = self.conv6(imageOut)
        imageOut = self.conv7(imageOut)
        imageOut = self.conv8(imageOut)
        imageOut = self.conv9(imageOut)
        imageOut = self.conv10(imageOut)
        imageOut = self.conv11(imageOut)
        imageOut = self.conv12(imageOut)

        if self.imagesize==128:
            imageOut = self.conv13_1(imageOut)
            imageOut = self.conv14_1(imageOut)
            imageOut = self.conv15_1(imageOut)
            imageOut = self.conv13(imageOut)

        else:

            imageOut = self.conv13(imageOut)

        imageOut = self.conv14(imageOut)               
        return imageOut

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )

#Build a Discriminator for GAN stack 

class Discriminator_V2(nn.Module):
    def __init__(self,label_length, ngpu=0, image_size=32, discriminator_mapping_size=0, channels=3):
        super(Discriminator_V2, self).__init__()

        
        self.checkDevice()

        self.ngpu = ngpu            
        self.image_size = image_size
        self.channels = channels

        # Habitualmente en el primer ejerciio 
        # label_length era 800

        self.l1 = nn.Linear(label_length, image_size*image_size*channels, bias=False)            
        self.conv1 = nn.Conv2d(2*channels, discriminator_mapping_size, 6, 2, 4, bias=False) 
        self.conv2 = nn.LeakyReLU(0.2, inplace=True)
        self.conv3 = nn.Conv2d(discriminator_mapping_size, discriminator_mapping_size * 2, 6, 2, 5, bias=False)
        self.conv4 = nn.BatchNorm2d(discriminator_mapping_size * 2)
        self.conv5 = nn.LeakyReLU(0.2, inplace=True)
        self.conv6 = nn.Conv2d(discriminator_mapping_size * 2, discriminator_mapping_size * 4, 6, 2, 4, bias=False)
        self.conv7 = nn.BatchNorm2d(discriminator_mapping_size * 4)
        self.conv8 = nn.LeakyReLU(0.2, inplace=True)
        self.conv9 = nn.Conv2d(discriminator_mapping_size * 4, discriminator_mapping_size * 8, 6, 2, 2, bias=False)
        self.conv10 = nn.BatchNorm2d(discriminator_mapping_size * 8)
        self.conv11 = nn.LeakyReLU(0.2, inplace=True)

        if self.image_size==128:
            self.conv12_1 = nn.Conv2d(discriminator_mapping_size * 8, 512, 6, 2, 2, bias=False)
            self.conv12_2 = nn.LeakyReLU(0.2, inplace=True)
                       
            self.conv12_3 = nn.Conv2d(512, 1, 6, 2, 1, bias=False)

        elif self.image_size==256:
            self.conv12_1_1 = nn.Conv2d(discriminator_mapping_size * 8, 512, 6, 2, 2, bias=False)
            self.conv12_2_1 = nn.LeakyReLU(0.2, inplace=True)
            self.conv10_1 = nn.BatchNorm2d(discriminator_mapping_size * 16)


            self.conv12_1_2 = nn.Conv2d(512, 1024, 6, 2, 2, bias=False)
            self.conv12_2_2 = nn.LeakyReLU(0.2, inplace=True)

            self.conv12_3 = nn.Conv2d(1024, 1, 6, 2, 1, bias=False)

        elif self.image_size==512:
            self.conv12_1_1 = nn.Conv2d(discriminator_mapping_size * 8, 512, 6, 2, 2, bias=False)
            self.conv12_2_1 = nn.LeakyReLU(0.2, inplace=True)
            self.conv10_1 = nn.BatchNorm2d(discriminator_mapping_size * 16)


            self.conv12_1_2 = nn.Conv2d(512, 1024, 6, 2, 2, bias=False)
            self.conv12_2_2 = nn.LeakyReLU(0.2, inplace=True)
            self.conv10_2 = nn.BatchNorm2d(discriminator_mapping_size * 32)

            self.conv12_1_3 = nn.Conv2d(1024, 2048, 2, 2, 1, bias=False)
            self.conv12_2_3 = nn.LeakyReLU(0.2, inplace=True)

            self.conv12_3 = nn.Conv2d(2048, 1, 6, 2, 1, bias=False)
        else:
            self.conv12 = nn.Conv2d(discriminator_mapping_size * 8, 1, 6, 1, 0, bias=False)

        self.conv13 = nn.Sigmoid()


    def forward(self, input, label, b_size):
        x1 = input
        x2 = self.l1(label) #Size must be taken care = 800 in this case
        #the output is imagesize x imagesize x channel
        #hence the need of reshape 

        if self.ngpu == 0 :
        
            x2 = x2.reshape(int(b_size),self.channels,self.image_size,self.image_size) 
        else:
            x2 = x2.reshape(int(b_size/self.ngpu),self.channels,self.image_size,self.image_size) 

        combine = torch.cat((x1,x2),dim=1) # concatenate in a given dimension
        #esto viene del mismo paper sobre los CGAN

        combine = self.conv1(combine) #This conv1 considers 2 x channels from the combine
        combine = self.conv2(combine)
        combine = self.conv3(combine)
        combine = self.conv4(combine)
        combine = self.conv5(combine)
        combine = self.conv6(combine)
        combine = self.conv7(combine)
        combine = self.conv8(combine)
        combine = self.conv9(combine)
        combine = self.conv10(combine)
        combine = self.conv11(combine)

        if self.image_size==128:
            combine = self.conv12_1(combine)
            combine = self.conv12_2(combine)
            combine = self.conv12_3(combine)
        elif self.image_size==256:

            combine = self.conv12_1_1(combine)
            combine = self.conv12_2_1(combine)
            combine = self.conv10_1(combine)

            combine = self.conv12_1_2(combine)
            combine = self.conv12_2_2(combine)
    

            combine = self.conv12_3(combine)
            #print(combine.shape)

        elif self.image_size==512:

            combine = self.conv12_1_1(combine)
            combine = self.conv12_2_1(combine)
            combine = self.conv10_1(combine)

            combine = self.conv12_1_2(combine)
            combine = self.conv12_2_2(combine)
            combine = self.conv10_2(combine)

            combine = self.conv12_1_3(combine)
            combine = self.conv12_2_3(combine)

            combine = self.conv12_3(combine)

        else:
            combine = self.conv12(combine)

        combine = self.conv13(combine)
        return combine

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    


class Predictor_CNN(nn.Module):
    def __init__(self, cond_input_size, ngpu=0, image_size=512 , output_size=0, channels=3,features_num=1000, hiden_num=5000, dropout=0.2, Y_prediction_size=601):
        super(Predictor_CNN, self).__init__()

        
        self.checkDevice()

        self.ngpu = ngpu            
        self.image_size = image_size
        self.channels = channels
        self.features_num = features_num
        self.dropout=dropout


        self.l1 = nn.Linear(cond_input_size, image_size*image_size*channels, bias=False)           
        self.conv1 = nn.Conv2d(2*channels, output_size, 6, 2, 4, bias=False) 
        self.conv2 = nn.LeakyReLU(0.2, inplace=True)
        self.conv3 = nn.Conv2d(output_size, output_size * 2, 6, 2, 5, bias=False)
        self.conv4 = nn.BatchNorm2d(output_size * 2)
        self.conv5 = nn.LeakyReLU(0.2, inplace=True)
        self.conv6 = nn.Conv2d(output_size * 2, output_size * 4, 6, 2, 4, bias=False)
        self.conv7 = nn.BatchNorm2d(output_size * 4)
        self.conv8 = nn.LeakyReLU(0.2, inplace=True)
        self.conv9 = nn.Conv2d(output_size * 4, output_size * 8, 6, 2, 2, bias=False)
        self.conv10 = nn.BatchNorm2d(output_size * 8)
        self.conv11 = nn.LeakyReLU(0.2, inplace=True)
        self.conv12 = nn.Conv2d(output_size * 8, output_size * 16, 2, 1, 0, bias=False)

        
        #Here we apply a flattening
        #10368
        #139392
        if image_size==128:
            self.l2 = nn.Linear(10368, hiden_num, bias=False)           

        elif image_size==512:
            self.l2 = nn.Linear(139392, hiden_num, bias=False)           
        elif image_size==64:
            self.l2 = nn.Linear(3200, hiden_num, bias=False)           
        
        #self.l3 = nn.Linear(hiden_num, features_num, bias=False)           
        self.dropout2 = nn.Dropout(dropout)
        self.l4 = nn.Linear(hiden_num, hiden_num, bias=False)           
        self.l5 = nn.Linear(hiden_num, hiden_num, bias=False)           
        self.l6 = nn.Linear(hiden_num, Y_prediction_size, bias=False)           


    def forward(self, input_, conditioning, b_size):
        x1 = input_
        x2 = self.l1(conditioning) #Size must be taken care = 800 in this case
        #the output is imagesize x imagesize x channel
        #hence the need of reshape 
        #print(x2.shape)
        if self.ngpu == 0 :
        
            x2 = x2.reshape(int(b_size),self.channels,self.image_size,self.image_size) 
        else:
            x2 = x2.reshape(int(b_size/self.ngpu),self.channels,self.image_size,self.image_size) 
        
        #print(x2.shape)

        combine = torch.cat((x1,x2),dim=1) # concatenate in a given dimension
     
        outmap_min, _ = torch.min(combine, dim=1, keepdim=True)
        outmap_max, _ = torch.max(combine, dim=1, keepdim=True)
        combine = (combine - outmap_min) / (outmap_max - outmap_min) 

        combine = self.conv1(combine) #This conv1 considers 2 x channels from the combine
        combine = self.conv2(combine)
        combine = self.conv3(combine)
        combine = self.conv4(combine)
        combine = self.conv5(combine)
        
        combine = self.conv6(combine)
        combine = self.conv7(combine)
        combine = self.conv8(combine)
        combine = self.conv9(combine)
        combine = self.conv10(combine)
        combine = self.conv11(combine)
        combine = self.conv12(combine)

        """Change between conv to linear layers"""

        combine =combine.view(combine.size(0), -1)
        combine = self.l2(combine)
        #combine = self.l3(combine)

        combine = self.dropout2(combine)

        combine = self.l4(combine)
        
        combine = self.dropout2(combine)

        combine = self.l5(combine)
        combine = self.l6(combine)

        #a Final softmax
        #combine = F.softmax(combine, dim=1)


        return combine

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    

class Predictor_RESNET(nn.Module):
    def __init__(self,resnet_arch,conditional, cond_input_size,cond_channels, ngpu=0, image_size=512 , output_size=0, channels=3,features_num=1000, hiden_num=5000, dropout=0.2, Y_prediction_size=601):
        super(Predictor_RESNET, self).__init__()

        
        self.checkDevice()

        self.ngpu = ngpu            
        self.image_size = image_size
        self.channels = channels
        self.features_num = features_num
        self.dropout=dropout
        self.cond_channels=cond_channels

        self.l1 = nn.Linear(cond_input_size, image_size*image_size*cond_channels, bias=False)           

        #weights = ResNet50_Weights.DEFAULT
        if resnet_arch=="resnet50":
            self.model = resnet50(pretrained=False)
        else:
            self.model = resnet152(pretrained=False)



        self.conditional=conditional
        num_filters = self.model.conv1.out_channels   
        kernel_size = self.model.conv1.kernel_size
        stride = self.model.conv1.stride
        padding = self.model.conv1.padding

        if self.conditional==True:
            conv1 = torch.nn.Conv2d(self.cond_channels+self.channels, num_filters, kernel_size=kernel_size, stride=stride, padding=padding)
            # Initialize the new conv1 layer's weights by averaging the pretrained weights across the channel dimension
            #original_weights = self.model.conv1.weight.data.mean(dim=1, keepdim=True)
            # Expand the averaged weights to the number of input channels of the new dataset
            #conv1.weight.data = original_weights.repeat(1, 6, 1, 1)
        else:
            conv1 = torch.nn.Conv2d(self.channels, num_filters, kernel_size=kernel_size, stride=stride, padding=padding)
            # Initialize the new conv1 layer's weights by averaging the pretrained weights across the channel dimension
            #original_weights = self.model.conv1.weight.data.mean(dim=1, keepdim=True)
            # Expand the averaged weights to the number of input channels of the new dataset
            #conv1.weight.data = original_weights.repeat(1, 3, 1, 1)        # Substitute the FC output layer

        self.model.conv1 = conv1

        self.linear = nn.Sequential(
                nn.Linear(self.model.fc.in_features, self.model.fc.in_features, bias=False),
                nn.Linear(self.model.fc.in_features, features_num, bias=False),
                nn.Linear(features_num, hiden_num, bias=False),
                nn.Dropout(dropout),
                nn.Linear(hiden_num, Y_prediction_size, bias=False)           
            )
        
        self.model.fc =self.linear
        
        #torch.nn.init.xavier_uniform_(self.model.fc.weight)


    def forward(self, input_, conditioning, b_size):
        x1 = input_
        #the output is imagesize x imagesize x channel
        #hence the need of reshape 
        #print(x2.shape)
        #We can tray as many channels as prefered. In this case I will try 1 channel
        num_channel=self.cond_channels

        if self.conditional:
            
            x2 = self.l1(conditioning) #Size must be taken care = 800 in this case
            m = nn.Tanh()
            x2 = m(x2)

            if self.ngpu == 0 :
            
                x2 = x2.reshape(int(b_size),num_channel,self.image_size,self.image_size) 
                
            else:
                x2 = x2.reshape(int(b_size/self.ngpu),num_channel,self.image_size,self.image_size)

            # if self.cond_channels==3:
            #     x2 = torchvision.transforms.Normalize([0.6, ], [0.3, ],[0.8,])(x2)
            # else:
            #     x2 = torchvision.transforms.Normalize([0.2, ], [0.1, ],[0.3,])(x2)


            combine = torch.cat((x1,x2),dim=1) # concatenate in a given dimension
        
            #outmap_min, _ = torch.min(combine, dim=1, keepdim=True)
            #outmap_max, _ = torch.max(combine, dim=1, keepdim=True)
            #combine = (combine - outmap_min) / (outmap_max - outmap_min) 

            combine = self.model(combine) #This conv1 considers 2 x channels from the combine
        
            """Change between conv to linear layers"""
            return combine
        else:
            return self.model(x1)

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    


class Predictor_RESNET_V2(nn.Module):
    def __init__(self,resnet_arch,conditional, cond_input_size,cond_channels, ngpu=0, image_size=512 , output_size=0, channels=3,features_num=1000, hiden_num=5000, dropout=0.2, Y_prediction_size=601):
        super(Predictor_RESNET_V2, self).__init__()

        
        self.checkDevice()

        self.ngpu = ngpu            
        self.image_size = image_size
        self.channels = channels
        self.features_num = features_num
        self.dropout=dropout
        self.cond_channels=cond_channels

        self.l1 = nn.Linear(cond_input_size, image_size*image_size*cond_channels, bias=False)           

        #weights = ResNet50_Weights.DEFAULT
        if resnet_arch=="resnet50":
            self.model = resnet50(pretrained=False)
        elif resnet_arch == "resnet18":
            self.model = resnet18(pretrained=False)

        else:
            self.model = resnet152(pretrained=False)



        self.conditional=conditional
        num_filters = self.model.conv1.out_channels   
        kernel_size = self.model.conv1.kernel_size
        stride = self.model.conv1.stride
        padding = self.model.conv1.padding

        if self.conditional==True:
            conv1 = torch.nn.Conv2d(self.cond_channels+self.channels, num_filters, kernel_size=kernel_size, stride=stride, padding=padding)
            # Initialize the new conv1 layer's weights by averaging the pretrained weights across the channel dimension
            #original_weights = self.model.conv1.weight.data.mean(dim=1, keepdim=True)
            # Expand the averaged weights to the number of input channels of the new dataset
            #conv1.weight.data = original_weights.repeat(1, 6, 1, 1)
        else:
            conv1 = torch.nn.Conv2d(self.channels, num_filters, kernel_size=kernel_size, stride=stride, padding=padding)
            # Initialize the new conv1 layer's weights by averaging the pretrained weights across the channel dimension
            #original_weights = self.model.conv1.weight.data.mean(dim=1, keepdim=True)
            # Expand the averaged weights to the number of input channels of the new dataset
            #conv1.weight.data = original_weights.repeat(1, 3, 1, 1)        # Substitute the FC output layer

        self.model.conv1 = conv1

        self.linear = nn.Sequential(
                nn.Linear(self.model.fc.in_features, features_num, bias=False),
                nn.Linear(features_num, hiden_num, bias=False),
                nn.Linear(hiden_num, Y_prediction_size, bias=False),  
                #nn.Tanh()
         
            )
        
        self.model.fc =self.linear
        
        #torch.nn.init.xavier_uniform_(self.model.fc.weight)


    def forward(self, input_, conditioning, b_size):
        x1 = input_
        #the output is imagesize x imagesize x channel
        #hence the need of reshape 
        #print(x2.shape)
        #We can tray as many channels as prefered. In this case I will try 1 channel
        num_channel=self.cond_channels

        if self.conditional:
            
            x2 = self.l1(conditioning) #Size must be taken care = 800 in this case
            m = nn.Tanh()
            x2 = m(x2)

            if self.ngpu == 0 :
            
                x2 = x2.reshape(int(b_size),num_channel,self.image_size,self.image_size) 
                
            else:
                x2 = x2.reshape(int(b_size/self.ngpu),num_channel,self.image_size,self.image_size)

            # if self.cond_channels==3:
            #     x2 = torchvision.transforms.Normalize([0.6, ], [0.3, ],[0.8,])(x2)
            # else:
            #     x2 = torchvision.transforms.Normalize([0.2, ], [0.1, ],[0.3,])(x2)


            combine = torch.cat((x1,x2),dim=1) # concatenate in a given dimension
        
            #outmap_min, _ = torch.min(combine, dim=1, keepdim=True)
            #outmap_max, _ = torch.max(combine, dim=1, keepdim=True)
            #combine = (combine - outmap_min) / (outmap_max - outmap_min) 

            combine = self.model(combine) #This conv1 considers 2 x channels from the combine
        
            """Change between conv to linear layers"""
            return combine
        else:
            return self.model(x1)

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    

class Fringe_RESNET_V2(nn.Module):
    def __init__(self,resnet_arch,conditional, ngpu=0, image_size=512 , output_size=0, channels=3,features_num=1000, hiden_num=5000, dropout=0.2, Y_prediction_size=601):
        super(Fringe_RESNET_V2, self).__init__()

        
        self.checkDevice()

        self.ngpu = ngpu            
        self.image_size = image_size
        self.channels = channels
        self.features_num = features_num
        self.dropout=dropout


        #weights = ResNet50_Weights.DEFAULT
        if resnet_arch=="resnet50":
            self.model = resnet50(pretrained=False)
        elif resnet_arch == "resnet18":
            self.model = resnet18(pretrained=False)

        else:
            self.model = resnet152(pretrained=False)



        self.conditional=conditional
        num_filters = self.model.conv1.out_channels   
        kernel_size = self.model.conv1.kernel_size
        stride = self.model.conv1.stride
        padding = self.model.conv1.padding

        if self.conditional==True:
            conv1 = torch.nn.Conv2d(self.cond_channels+self.channels, num_filters, kernel_size=kernel_size, stride=stride, padding=padding)
            # Initialize the new conv1 layer's weights by averaging the pretrained weights across the channel dimension
            #original_weights = self.model.conv1.weight.data.mean(dim=1, keepdim=True)
            # Expand the averaged weights to the number of input channels of the new dataset
            #conv1.weight.data = original_weights.repeat(1, 6, 1, 1)
        else:
            conv1 = torch.nn.Conv2d(self.channels, num_filters, kernel_size=kernel_size, stride=stride, padding=padding)
            # Initialize the new conv1 layer's weights by averaging the pretrained weights across the channel dimension
            #original_weights = self.model.conv1.weight.data.mean(dim=1, keepdim=True)
            # Expand the averaged weights to the number of input channels of the new dataset
            #conv1.weight.data = original_weights.repeat(1, 3, 1, 1)        # Substitute the FC output layer

        self.model.conv1 = conv1

        self.linear = nn.Sequential(
                nn.Linear(self.model.fc.in_features, features_num, bias=False),
                nn.Linear(features_num, hiden_num, bias=False),
                nn.Linear(hiden_num, Y_prediction_size, bias=False),  
                #nn.Tanh()
         
            )
        
        self.model.fc =self.linear
        
        #torch.nn.init.xavier_uniform_(self.model.fc.weight)


    def forward(self, input_):
        x1 = input_
      
        return self.model(x1)

    def checkDevice(self):
        self.device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
        )
    


class Diffusion:

    def __init__(self,device, noise_steps=1000, beta_start=1e-4, beta_end=0.02, img_size=64 ):
        self.noise_steps = noise_steps
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.img_size = img_size
        self.device = device

        self.beta = self.prepare_noise_schedule().to(device) #prepares noise for every step
        self.alpha = 1. - self.beta #calc alpha for every beta step
        self.alpha_hat = torch.cumprod(self.alpha, dim=0) #get alpha hat which is the producof all alphas

    def prepare_noise_schedule(self):
        #this creates a linear distribution of beta along the time steps
        """pending! implement cosine beta distribution"""

        return torch.linspace(self.beta_start, self.beta_end, self.noise_steps)

    def noise_images(self, x, t):

        #X_t sample in any arbitrary time
        #one way to do this is by adding noise step by step 
        #the other way is to doit all at once
        sqrt_alpha_hat = torch.sqrt(self.alpha_hat[t])[:, None, None, None]
        sqrt_one_minus_alpha_hat = torch.sqrt(1 - self.alpha_hat[t])[:, None, None, None]

        #noise
        Ɛ = torch.randn_like(x)
        return sqrt_alpha_hat * x + sqrt_one_minus_alpha_hat * Ɛ, Ɛ

    def sample_timesteps(self, n):
#
        return torch.randint(low=1, high=self.noise_steps, size=(n,))



    """This corresponds to Algorithm Sampling"""
    """We need to sample in reverse direction
    This means from a X_t value, to obtain the previous step.
    And finally obtain X_0"""

    def sample(self, model, n):
        logging.info(f"Sampling {n} new images....")

        model.eval() #Model used for sampling

        with torch.no_grad():

            """Generate n images with 3 channels."""
            x = torch.randn((n, 3, self.img_size, self.img_size)).to(self.device) #create initial images with random noise

            for i in tqdm(reversed(range(1, self.noise_steps)), position=0): #loop over time steps

                t = (torch.ones(n) * i).long().to(self.device)

                predicted_noise = model(x, t)
                alpha = self.alpha[t][:, None, None, None]
                alpha_hat = self.alpha_hat[t][:, None, None, None]
                beta = self.beta[t][:, None, None, None]

                #Excluding the first images?!
                if i > 1:
                    noise = torch.randn_like(x) #Returns a tensor with the same size as input that is filled with random numbers from a normal distribution with mean 0 and variance 1.
                else:
                    noise = torch.zeros_like(x)#Returns a tensor with the same size as input that is filled with random numbers from a normal distribution with mean 0 and variance 1.

                #This is the cool formula with epsilon namely the noise perturbation
                #Removing a little noise in each step
                x = 1 / torch.sqrt(alpha) * (x - ((1 - alpha) / (torch.sqrt(1 - alpha_hat))) * predicted_noise) + torch.sqrt(beta) * noise

        model.train()
        x = (x.clamp(-1, 1) + 1) / 2 #make all values between 0 and 1 
        x = (x * 255).type(torch.uint8) #valid pixel range
        return x
    

    #Sample conditional diffusion
    def sample_cdm(self, model, n, labels, cfg_scale=3):
        logging.info(f"Sampling {n} new images....")
        model.eval()
        with torch.no_grad():
            x = torch.randn((n, 3, self.img_size, self.img_size)).to(self.device)
            for i in tqdm(reversed(range(1, self.noise_steps)), position=0):
                t = (torch.ones(n) * i).long().to(self.device)
                predicted_noise = model(x, t, labels)

                #This is to enable CFG conditional fre guidance
                #torch lerp interpolates the unconditional predicted noise

                if cfg_scale > 0:
                    uncond_predicted_noise = model(x, t, None)
                    predicted_noise = torch.lerp(uncond_predicted_noise, predicted_noise, cfg_scale)

                alpha = self.alpha[t][:, None, None, None]
                alpha_hat = self.alpha_hat[t][:, None, None, None]
                beta = self.beta[t][:, None, None, None]
                if i > 1:
                    noise = torch.randn_like(x)
                else:
                    noise = torch.zeros_like(x)
                x = 1 / torch.sqrt(alpha) * (x - ((1 - alpha) / (torch.sqrt(1 - alpha_hat))) * predicted_noise) + torch.sqrt(beta) * noise
        model.train()
        x = (x.clamp(-1, 1) + 1) / 2
        x = (x * 255).type(torch.uint8)
        return x



"""Stable difussion stack"""
class DiffusionWrapper(nn.Module):
    def __init__(self, diffusion_model: toolkit.UNetModel):
        super().__init__()
        self.diffusion_model = diffusion_model

    def forward(self, x: torch.Tensor, time_steps: torch.Tensor, context: torch.Tensor):
        return self.diffusion_model(x, time_steps, context)

class StableDiffusion(nn.Module):
    
    model: DiffusionWrapper
    first_stage_model: toolkit.Autoencoder
    cond_stage_model: toolkit.CLIPTextEmbedder
    
    def __init__(self,
                 unet_model: toolkit.UNetModel ,
                 autoencoder: toolkit.Autoencoder,
                 clip_embedder: toolkit.CLIPTextEmbedder,
                 latent_scaling_factor: float,
                 n_steps: int,
                 linear_start: float,
                 linear_end: float,
                 ):
        # unet_model is the U-Net that predicts noise ϵ_cond(x_t,c), in latent space
        # autoencoder is the AutoEncoder
        # clip_embedder is the CLIP embeddings generator
        # latent_scaling_factor is the scaling factor for the latent space. The encodings of the autoencoder are scaled by this before feeding into the U-Net.
        # n_steps is the number of diffusion steps T.
        # linear_start is the start of the β schedule.
        # linear_end is the end of the β schedule.
        super().__init__()
        self.model = DiffusionWrapper(unet_model)

        self.first_stage_model = autoencoder
        self.latent_scaling_factor = latent_scaling_factor
        self.cond_stage_model = clip_embedder 

        self.n_steps = n_steps #Number of steps T

        #ß scheduler
        beta = torch.linspace(linear_start ** 0.5, linear_end ** 0.5, n_steps, dtype=torch.float64) ** 2
        self.beta = nn.Parameter(beta.to(torch.float32), requires_grad=False)

        alpha = 1. - beta
        alpha_bar = torch.cumprod(alpha, dim=0)
        self.alpha_bar = nn.Parameter(alpha_bar.to(torch.float32), requires_grad=False)
        
    @property
    def device(self):
        return next(iter(self.model.parameters())).device
    
    def get_text_conditioning(self, prompts: list[str]):    
        
        return self.cond_stage_model(prompts)
    
   #Get scaled latent space representation of the image
    #The encoder output is a distribution. We sample from that and multiply by the scaling factor.
    def autoencoder_encode(self, image: torch.Tensor):
        return self.latent_scaling_factor * self.first_stage_model.encode(image).sample()
    
    #Get image from the latent representation
    #   We scale down by the scaling factor and then decode.
    def autoencoder_decode(self, z: torch.Tensor):
        return self.first_stage_model.decode(z / self.latent_scaling_factor)
    
    #Predict noise given the latent representation xt, time step t, and the conditioning context c.
    def forward(self, x: torch.Tensor, t: torch.Tensor, context: torch.Tensor):
        return self.model(x, t, context)



"""Vision Transformer"""
"""PRE LN architecture"""

"""PRE LN architecture"""

class AttentionBlock(nn.Module):
    def __init__(self, embed_dim, hidden_dim, num_heads, dropout=0.0):
        """Attention Block.

        Args:
            embed_dim: Dimensionality of input and attention feature vectors
            hidden_dim: Dimensionality of hidden layer in feed-forward network
                         (usually 2-4x larger than embed_dim)
            num_heads: Number of heads to use in the Multi-Head Attention block
            dropout: Amount of dropout to apply in the feed-forward network
        """
        super().__init__()

        self.layer_norm_1 = nn.LayerNorm(embed_dim)
        self.attn = nn.MultiheadAttention(embed_dim, num_heads)
        self.layer_norm_2 = nn.LayerNorm(embed_dim)
        self.linear = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        inp_x = self.layer_norm_1(x)
        x = x + self.attn(inp_x, inp_x, inp_x)[0]
        x = self.layer_norm_2(x)

        x = x + self.linear(x)
        return x
    
class VisionTransformer(nn.Module):
    def __init__(
        self,
       **kwargs
    ):

        """Vision Transformer.

        Args:
            embed_dim: Dimensionality of the input feature vectors to the Transformer
            hidden_dim: Dimensionality of the hidden layer in the feed-forward networks
                         within the Transformer usually 2-4x larger than embed_dim
            num_channels: Number of channels of the input (3 for RGB)
            num_heads: Number of heads to use in the Multi-Head Attention block
            num_layers: Number of layers to use in the Transformer
            num_classes: Number of classes to predict
            patch_size: Number of pixels that the patches have per dimension
            num_patches: Maximum number of patches an image can have
            dropout: Amount of dropout to apply in the feed-forward network and
                      on the input encoding
        """
        super().__init__()
        
        
        self.batch_size=kwargs["batch_size"]
        embed_dim=kwargs["embed_dim"]
        hidden_dim=kwargs["hidden_dim"]
        self.num_channels=kwargs["num_channels"]
        self.cond_num_channels=kwargs["con_num_channels"]
        num_heads=kwargs["num_heads"]
        num_layers=kwargs["num_layers"]
        num_classes=kwargs["num_classes"]
        patch_size=kwargs["patch_size"]
        num_patches=kwargs["num_patches"]
        dropout=kwargs["dropout"]
        self.image_size=kwargs["image_size"]
        self.regression=kwargs["regression"]

        self.patch_size = patch_size
        self.ngpu=0

        if kwargs['conditionalIn'] == True :

            print('conditioned')
            self.conditionalIn=kwargs["conditionalIn"]
            self.conditionalLen=kwargs["conditionalLen"]

            self.l1 = nn.Linear(self.conditionalLen, self.image_size*self.image_size*self.cond_num_channels, bias=False)           


            # Layers/Networks
            
            self.input_layer = nn.Linear((self.cond_num_channels+self.num_channels) * (patch_size**2), 2*embed_dim)
            self.transformer = nn.Sequential(
                *(AttentionBlock(2*embed_dim, hidden_dim, num_heads, dropout=dropout) for _ in range(num_layers))
            )


            # If regression or classification
            if self.regression:
                self.mlp_head = nn.Sequential(
                    nn.LayerNorm(2*embed_dim),
                    nn.Linear(2*embed_dim, 2*embed_dim, bias=False),
                    nn.Dropout(dropout),
                    nn.Linear(2*embed_dim, num_classes, bias=False) 
                )

            else:
                self.mlp_head = nn.Sequential(nn.LayerNorm(2*embed_dim), nn.Linear(2*embed_dim, num_classes))

            self.dropout = nn.Dropout(dropout)

            # Parameters/Embeddings
            #self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim))
            
            self.cls_token = nn.Parameter(torch.randn(self.batch_size, 1, (self.cond_num_channels+self.num_channels) * (patch_size)**2))
            
            
            self.pos_embedding = nn.Parameter(torch.randn(self.batch_size, 1 + num_patches, 2*embed_dim))



        else:
            # Layers/Networks
            
            self.input_layer = nn.Linear(self.num_channels * (patch_size**2), embed_dim)
            self.transformer = nn.Sequential(
                *(AttentionBlock(embed_dim, hidden_dim, num_heads, dropout=dropout) for _ in range(num_layers))
            )

            # If regression or classification

            if self.regression:
                self.mlp_head = nn.Sequential(
                    nn.LayerNorm(2*embed_dim),
                    nn.Linear(2*embed_dim, 2*embed_dim, bias=False),
                    nn.Dropout(dropout),
                    nn.Linear(2*embed_dim, num_classes, bias=False) 
                )

            else:
                self.mlp_head = nn.Sequential(nn.LayerNorm(embed_dim),
                                              nn.Linear(embed_dim, embed_dim),
                                              nn.Linear(embed_dim, num_classes))
            
            self.dropout = nn.Dropout(dropout)

            # Parameters/Embeddings
            #self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim))
            
            self.cls_token = nn.Parameter(torch.randn(self.batch_size, 1, self.num_channels * patch_size**2))
            
            
            self.pos_embedding = nn.Parameter(torch.randn(self.batch_size, 1 + num_patches, embed_dim))

        #self.apply(self._init_weights) 

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.trunc_normal_(m.weight, std=.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def patchify(self,x, patch_size, flatten_channels):
        """
        Args:
            x: Tensor representing the image of shape [B, C, H, W]
            patch_size: Number of pixels per dimension of the patches (integer)
            flatten_channels: If True, the patches will be returned in a flattened format
                            as a feature vector instead of a image grid.
        """
            
        B, C, H, W = x.shape
        x = x.reshape(B, C, H // patch_size, patch_size, W // patch_size, patch_size)
        x = x.permute(0, 2, 4, 1, 3, 5)  # [B, H', W', C, p_H, p_W]
        x = x.flatten(1, 2)  # [B, H'*W', C, p_H, p_W]
        if flatten_channels:
            x = x.flatten(2, 4)  # [B, H'*W', C*p_H*p_W]
            """Batches, number of patches per image, each flattened patch size including  channel"""
        return x  
        
    def forward(self, x, condition=None):
        # Preprocess input
        #x = img_to_patch(x, self.patch_size)
        if condition !=None:
 
            x2 = self.l1(condition) 

            if self.ngpu == 0 :
            
                x2 = x2.reshape(int(self.batch_size),self.cond_num_channels,self.image_size,self.image_size) 
            else:
                x2 = x2.reshape(int(self.batch_size/self.ngpu),self.cond_num_channels,self.image_size,self.image_size) 
            
            x2 = torchvision.transforms.Normalize([0.15, ], [.1, ],[0.4,])(x2)

            combine = torch.cat((x,x2),dim=1) # concatenate in a given dimension
            
 
            outmap_min, _ = torch.min(combine, dim=1, keepdim=True)
            outmap_max, _ = torch.max(combine, dim=1, keepdim=True)
            x = (combine - outmap_min) / (outmap_max - outmap_min) 
    
        B, T, _, _ = x.shape


        x = self.patchify(x, patch_size=self.patch_size, flatten_channels=True)
        x = self.input_layer(x)

        # Add CLS token and positional encoding
        cls_token = self.cls_token #.repeat(B, 1, 1)
        #print("CLS Token  ",cls_token.shape)

        x = torch.cat([cls_token, x], dim=1)

        pos_embed=self.pos_embedding
        #print("Positional Embedd ",pos_embed.shape)
        
        x = x + pos_embed
        #print("x ", x.shape)
        # Apply Transforrmer
        x = self.dropout(x)
        x = x.transpose(0, 1)
        x = self.transformer(x)

        
        # Perform classification prediction
        cls = x[0]

        # If regression or classification
        # with if in case necessary in the future
        if self.regression:

            out = self.mlp_head(cls)

        else:
            out = self.mlp_head(cls)

        return out
    
    