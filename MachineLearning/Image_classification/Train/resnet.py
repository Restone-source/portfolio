import torch
import pytorch_lightning as pl
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import transforms
import torchvision.models as models
from torchvision.datasets import ImageFolder
from pytorch_lightning.plugins.environments import ClusterEnvironment

from argparse import ArgumentParser
from pathlib import Path
import os

class myResnetModel(pl.LightningModule):
    def __init__(self, num_classes, resnet_version, train_path, vld_path, test_path=None, batch_size=32):
        super().__init__()
        resnets = {
            18: models.resnet18, 34: models.resnet34,
            50: models.resnet50, 101: models.resnet101,
            152: models.resnet152
        }
        self.criterion = nn.BCEWithLogitsLoss()
        self.model = resnets[resnet_version](weights=None)
        self.train_path = train_path
        self.vld_path = vld_path
        self.test_path = test_path
        self.batch_size = batch_size
        # linear_size = list(self.resnet_model.children())[-1].in_features
        # self.model.fc = nn.Linear(linear_size, num_classes) # 마지막 레이어를 num_classes로 변경 (이미지 분류 개수) # default 1000

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y)
        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y)
        self.log("val_loss", loss, on_epoch=True, prog_bar=True, logger=True)

    def test_step(self, batch, batch_idx):
        x, y = batch
        preds = self(x)
        loss = self.criterion(preds, y)
        self.log("test_loss", loss, on_step=True, prog_bar=True, logger=True)

    def train_dataloader(self):
        resize_train_mean=[0.48109725, 0.4574676, 0.4078484]
        resize_train_std=[0.21910407, 0.21485911, 0.21586362]
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomCrop(220),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
            transforms.RandomHorizontalFlip(p = 0.2),
            transforms.RandomVerticalFlip(p = 0.2),
            transforms.ToTensor(),
            transforms.Normalize(resize_train_mean, resize_train_std)
        ])
        dataset = ImageFolder(self.train_path, transform=transform)
        loader = DataLoader(
            dataset=dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=4
        )
        return loader

    def val_dataloader(self):
        resize_train_mean=[0.48109725, 0.4574676, 0.4078484]
        resize_train_std=[0.21910407, 0.21485911, 0.21586362]
        transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(resize_train_mean, resize_train_std)
        ])
        dataset = ImageFolder(root=self.vld_path, transform=transform)
        loader = DataLoader(
            dataset=dataset,
            batch_size=1,
            shuffle=False,
            num_workers=4
        )
        return loader

    def test_dataloader(self):
        resize_train_mean=[0.48109725, 0.4574676, 0.4078484]
        resize_train_std=[0.21910407, 0.21485911, 0.21586362]
        transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(resize_train_mean, resize_train_std)
        ])
        img_test = ImageFolder(self.test_path, transform=transform)
        return DataLoader(img_test, batch_size=1, shuffle=False)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("model", type=int)
    parser.add_argument("num_classes", type=int)
    parser.add_argument("num_epochs", type=int)
    parser.add_argument("train_set", type=Path)
    parser.add_argument("vld_set", type=Path)
    parser.add_argument("nnode", type=int)
    parser.add_argument("gpus_per_node", type=int)
    parser.add_argument("-ts", "--test_set", type=Path, default=None)
    parser.add_argument("-b", "--batch_size", type=int, default=32)
    args = parser.parse_args()

    model = myResnetModel(resnet_version = args.model, num_classes = args.num_classes, train_path = args.train_set, vld_path = args.vld_set, test_path = args.test_set,batch_size = args.batch_size)
    trainer = pl.Trainer(accelerator="gpu", devices=args.gpus_per_node, num_nodes=args.nnode, max_epochs = args.num_epochs, precision=16, strategy="ddp")
    trainer.fit(model)

    save_path = "/models/" + 'trained_model.ckpt'
    trainer.save_checkpoint(save_path)

# python resnet.py 152 1000 10 /home/ant/data/train_img /home/ant/data/val_img 2 1 '10.0.0.4' 1024

