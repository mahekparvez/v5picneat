"""
Food Classification Model Training Script

Trains EfficientNet-B3 on WWEIA food dataset.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import albumentations as A
from albumentations.pytorch import ToTensorV2
import json
from pathlib import Path
from tqdm import tqdm
import wandb
from datetime import datetime
import argparse


class AlbumentationsDataset(torch.utils.data.Dataset):
    """Wrapper for using Albumentations with PyTorch."""
    
    def __init__(self, dataset, transform=None):
        self.dataset = dataset
        self.transform = transform
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        image, label = self.dataset[idx]
        
        # Convert PIL to numpy
        import numpy as np
        image = np.array(image)
        
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
        
        return image, label


class FoodClassifierTrainer:
    def __init__(
        self,
        data_dir: str = "data/processed",
        output_dir: str = "models",
        model_name: str = "efficientnet_b3",
        num_epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        device: str = None,
        use_wandb: bool = True
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.model_name = model_name
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.use_wandb = use_wandb
        
        # Device
        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"Using device: {self.device}")
        
        # Load class names
        with open(self.data_dir / "class_names.json") as f:
            self.class_names = json.load(f)
        
        self.num_classes = len(self.class_names)
        print(f"Number of classes: {self.num_classes}")
        
        # Initialize tracking
        self.best_val_acc = 0.0
        self.history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
    
    def get_transforms(self):
        """Get training and validation transforms."""
        train_transform = A.Compose([
            A.RandomResizedCrop(224, 224, scale=(0.8, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.3),
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.3),
            A.Rotate(limit=15, p=0.3),
            A.GaussianBlur(blur_limit=3, p=0.2),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        val_transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        return train_transform, val_transform
    
    def get_dataloaders(self):
        """Create train and validation dataloaders."""
        train_transform, val_transform = self.get_transforms()
        
        # Load datasets
        train_dataset_base = datasets.ImageFolder(self.data_dir / "train")
        val_dataset_base = datasets.ImageFolder(self.data_dir / "val")
        
        # Wrap with Albumentations
        train_dataset = AlbumentationsDataset(train_dataset_base, train_transform)
        val_dataset = AlbumentationsDataset(val_dataset_base, val_transform)
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )
        
        print(f"Train samples: {len(train_dataset)}")
        print(f"Val samples: {len(val_dataset)}")
        
        return train_loader, val_loader
    
    def create_model(self):
        """Create EfficientNet-B3 model."""
        # Load pretrained EfficientNet-B3
        model = models.efficientnet_b3(pretrained=True)
        
        # Modify classifier head
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, self.num_classes)
        )
        
        model = model.to(self.device)
        
        print(f"Model: {self.model_name}")
        print(f"Parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M")
        
        return model
    
    def train_epoch(self, model, train_loader, criterion, optimizer, scheduler):
        """Train for one epoch."""
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc="Training")
        for images, labels in pbar:
            images, labels = images.to(self.device), labels.to(self.device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                "loss": f"{running_loss / (pbar.n + 1):.4f}",
                "acc": f"{100. * correct / total:.2f}%"
            })
        
        scheduler.step()
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    @torch.no_grad()
    def validate(self, model, val_loader, criterion):
        """Validate the model."""
        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(val_loader, desc="Validation")
        for images, labels in pbar:
            images, labels = images.to(self.device), labels.to(self.device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                "loss": f"{running_loss / (pbar.n + 1):.4f}",
                "acc": f"{100. * correct / total:.2f}%"
            })
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def save_checkpoint(self, model, epoch, val_acc, is_best=False):
        """Save model checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "val_acc": val_acc,
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "model_name": self.model_name
        }
        
        # Save latest
        checkpoint_path = self.output_dir / "latest_model.pth"
        torch.save(checkpoint, checkpoint_path)
        
        # Save best
        if is_best:
            best_path = self.output_dir / "best_model.pth"
            torch.save(checkpoint, best_path)
            print(f"✓ Saved best model (val_acc: {val_acc:.2f}%)")
        
        # Save production model (state_dict only)
        if is_best:
            prod_checkpoint = {
                "model_state_dict": model.state_dict(),
                "num_classes": self.num_classes,
                "class_names": self.class_names
            }
            prod_path = self.output_dir / "food_classifier.pth"
            torch.save(prod_checkpoint, prod_path)
    
    def train(self):
        """Main training loop."""
        print("\n" + "=" * 60)
        print("Starting Training")
        print("=" * 60 + "\n")
        
        # Initialize W&B
        if self.use_wandb:
            wandb.init(
                project="pic-n-eat-v2",
                name=f"{self.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                config={
                    "model": self.model_name,
                    "num_classes": self.num_classes,
                    "epochs": self.num_epochs,
                    "batch_size": self.batch_size,
                    "learning_rate": self.learning_rate
                }
            )
        
        # Create dataloaders
        train_loader, val_loader = self.get_dataloaders()
        
        # Create model
        model = self.create_model()
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=self.learning_rate, weight_decay=0.01)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=self.num_epochs)
        
        # Training loop
        for epoch in range(self.num_epochs):
            print(f"\nEpoch {epoch + 1}/{self.num_epochs}")
            print("-" * 60)
            
            # Train
            train_loss, train_acc = self.train_epoch(
                model, train_loader, criterion, optimizer, scheduler
            )
            
            # Validate
            val_loss, val_acc = self.validate(model, val_loader, criterion)
            
            # Save history
            self.history["train_loss"].append(train_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_loss"].append(val_loss)
            self.history["val_acc"].append(val_acc)
            
            # Log to W&B
            if self.use_wandb:
                wandb.log({
                    "train_loss": train_loss,
                    "train_acc": train_acc,
                    "val_loss": val_loss,
                    "val_acc": val_acc,
                    "learning_rate": optimizer.param_groups[0]['lr']
                })
            
            # Save checkpoint
            is_best = val_acc > self.best_val_acc
            if is_best:
                self.best_val_acc = val_acc
            
            self.save_checkpoint(model, epoch, val_acc, is_best)
            
            print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            print(f"Best Val Acc: {self.best_val_acc:.2f}%")
        
        # Save training history
        with open(self.output_dir / "training_history.json", 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ Training Complete! Best Val Acc: {self.best_val_acc:.2f}%")
        print("=" * 60)
        
        if self.use_wandb:
            wandb.finish()


def main():
    parser = argparse.ArgumentParser(description="Train food classification model")
    parser.add_argument("--data_dir", default="data/processed", help="Path to processed data")
    parser.add_argument("--output_dir", default="models", help="Output directory for models")
    parser.add_argument("--model", default="efficientnet_b3", help="Model architecture")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--device", default=None, help="Device (cuda/cpu)")
    parser.add_argument("--no-wandb", action="store_true", help="Disable W&B logging")
    
    args = parser.parse_args()
    
    trainer = FoodClassifierTrainer(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        model_name=args.model,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device,
        use_wandb=not args.no_wandb
    )
    
    trainer.train()


if __name__ == "__main__":
    main()
