
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torchvision import transforms
import pytorch_lightning as pl
import torchvision.datasets
import json
import torchvision.models

# imagenet_class_index = json.load(open('/home/ant/imagenet_class_index.json'))
resize_train_mean=[0.48109725, 0.4574676, 0.4078484]
resize_train_std=[0.21910407, 0.21485911, 0.21586362]

# Image Normalization
transform_train = transforms.Compose([
    transforms.Resize((255)), # 이미지 resize
    transforms.RandomCrop(224), # 이미지를 랜덤으로 크롭
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2), # 이미지 지터링(밝기, 대조, 채비, 색조)
    transforms.RandomHorizontalFlip(p = 0.9), # p확률로 이미지 좌우반전
    transforms.RandomVerticalFlip(p = 0.9), # p확률로 상하반전
    transforms.ToTensor(),
    transforms.Normalize(resize_train_mean, resize_train_std)
])

class LitAutoEncoder(pl.LightningModule):
	def __init__(self):
		super().__init__()
		self.encoder = nn.Sequential(
      nn.Linear(28 * 28, 64),
      nn.ReLU(),
      nn.Linear(64, 3))
		self.decoder = nn.Sequential(
      nn.Linear(3, 64),
      nn.ReLU(),
      nn.Linear(64, 28 * 28))

	def forward(self, x):
		embedding = self.encoder(x)
		return embedding

	def configure_optimizers(self):
		optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
		return optimizer

	def training_step(self, train_batch, batch_idx):
		x, y = train_batch
		x = x.view(x.size(0), -1)
		z = self.encoder(x)    
		x_hat = self.decoder(z)
		loss = F.mse_loss(x_hat, x)
		self.log('train_loss', loss)
		return loss

	def validation_step(self, val_batch, batch_idx):
		x, y = val_batch
		x = x.view(x.size(0), -1)
		z = self.encoder(x)
		x_hat = self.decoder(z)
		loss = F.mse_loss(x_hat, x)
		self.log('val_loss', loss)

# data
print("STEP Create dataset")
trainset = torchvision.datasets.ImageFolder(root='/data/trainimage/images/', transform=transform_train)
trainsetval = torchvision.datasets.ImageFolder(root='/data/ILSVRC2012_img_val/', transform=transform_train)

print("STEP Dataload")
train_loader = DataLoader(trainset, batch_size=32)
val_loader = DataLoader(trainsetval, batch_size=32)

# dataset = MNIST('', train=True, download=True, transform=transforms.ToTensor())
# mnist_train, mnist_val = random_split(dataset, [55000, 5000])

# train_loader = DataLoader(mnist_train, batch_size=32)
# val_loader = DataLoader(mnist_val, batch_size=32)

# model
print("STEP Define Model")
model = LitAutoEncoder()
# model = torchvision.models.densenet121()
# model.eval()
# model.train()

# training
# trainer = pl.Trainer(gpus=4, num_nodes=8, precision=16, limit_train_batches=0.5)
print("START Trainng")
# trainer = pl.Trainer(accelerator='gpu', devices=1, num_nodes=1, precision=16, limit_train_batches=0.5)
trainer = pl.Trainer(accelerator='gpu', devices=1)
trainer.fit(model, train_loader, val_loader)

print("END Trainng")