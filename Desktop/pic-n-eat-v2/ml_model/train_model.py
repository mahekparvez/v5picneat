"""
Custom Food Recognition Model for Pic N Eat
Uses EfficientNet-B3 as backbone with custom head for food classification
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import timm
from PIL import Image
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
from typing import Tuple, Dict, List
import albumentations as A
from albumentations.pytorch import ToTensorV2

class FoodDataset(Dataset):
    """Custom dataset for food images"""
    
    def __init__(self, csv_file: str, transform=None, is_training: bool = True):
        self.data = pd.read_csv(csv_file)
        self.transform = transform
        self.is_training = is_training
        
        # Create label mapping
        self.classes = sorted(self.data['category'].unique().tolist())
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.idx_to_class = {idx: cls for cls, idx in self.class_to_idx.items()}
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        img_path = self.data.iloc[idx]['image_path']
        category = self.data.iloc[idx]['category']
        label = self.class_to_idx[category]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        image = np.array(image)
        
        if self.transform:
            transformed = self.transform(image=image)
            image = transformed['image']
        
        return image, label, category

def get_transforms(image_size: int = 384, is_training: bool = True):
    """Get augmentation transforms"""
    
    if is_training:
        return A.Compose([
            A.RandomResizedCrop(image_size, image_size, scale=(0.8, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.3),
            A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=15, p=0.3),
            A.OneOf([
                A.GaussNoise(var_limit=(10, 50)),
                A.GaussianBlur(),
                A.MotionBlur(),
            ], p=0.2),
            A.CoarseDropout(max_holes=8, max_height=32, max_width=32, p=0.3),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    else:
        return A.Compose([
            A.Resize(image_size, image_size),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])

class FoodRecognitionModel(nn.Module):
    """
    Custom food recognition model
    Uses EfficientNet-B3 backbone with attention mechanism
    """
    
    def __init__(self, num_classes: int, pretrained: bool = True):
        super().__init__()
        
        # Load EfficientNet-B3 as backbone
        self.backbone = timm.create_model(
            'efficientnet_b3',
            pretrained=pretrained,
            num_classes=0,  # Remove classifier
            global_pool=''  # Remove global pooling
        )
        
        # Get feature dimension
        with torch.no_grad():
            dummy_input = torch.randn(1, 3, 384, 384)
            features = self.backbone(dummy_input)
            self.feature_dim = features.shape[1]
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Conv2d(self.feature_dim, self.feature_dim // 8, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(self.feature_dim // 8, 1, 1),
            nn.Sigmoid()
        )
        
        # Global pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        
        # Classifier head
        self.classifier = nn.Sequential(
            nn.Linear(self.feature_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, x):
        # Extract features
        features = self.backbone(x)
        
        # Apply attention
        attention_weights = self.attention(features)
        features = features * attention_weights
        
        # Global pooling
        features = self.global_pool(features)
        features = features.flatten(1)
        
        # Classification
        output = self.classifier(features)
        
        return output

class FoodRecognitionTrainer:
    """Trainer for food recognition model"""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        lr: float = 1e-4,
        weight_decay: float = 1e-5
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        
        # Loss function with label smoothing
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        
        # Optimizer with different learning rates for backbone and head
        backbone_params = list(self.model.backbone.parameters())
        other_params = [
            p for n, p in self.model.named_parameters()
            if not n.startswith('backbone')
        ]
        
        self.optimizer = optim.AdamW([
            {'params': backbone_params, 'lr': lr * 0.1},  # Lower LR for pretrained backbone
            {'params': other_params, 'lr': lr}
        ], weight_decay=weight_decay)
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer, T_0=10, T_mult=2
        )
        
        self.best_val_acc = 0.0
        self.history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
    def train_epoch(self) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc='Training')
        for images, labels, _ in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            # Metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100. * correct / total:.2f}%'
            })
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    @torch.no_grad()
    def validate(self) -> Tuple[float, float]:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels, _ in tqdm(self.val_loader, desc='Validation'):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def train(self, epochs: int, save_dir: str = "./checkpoints"):
        """Train the model"""
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)
        
        print(f"🚀 Starting training on {self.device}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        
        for epoch in range(epochs):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch + 1}/{epochs}")
            print(f"{'='*60}")
            
            # Train
            train_loss, train_acc = self.train_epoch()
            
            # Validate
            val_loss, val_acc = self.validate()
            
            # Update scheduler
            self.scheduler.step()
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                    'class_to_idx': self.train_loader.dataset.class_to_idx
                }
                torch.save(checkpoint, save_dir / 'best_model.pth')
                print(f"✅ Saved new best model (Val Acc: {val_acc:.2f}%)")
        
        # Save training history
        with open(save_dir / 'training_history.json', 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"\n🎉 Training complete! Best validation accuracy: {self.best_val_acc:.2f}%")

def main():
    # Hyperparameters
    BATCH_SIZE = 32
    EPOCHS = 50
    IMAGE_SIZE = 384
    LEARNING_RATE = 1e-4
    
    # Load datasets
    train_dataset = FoodDataset(
        'data/train.csv',
        transform=get_transforms(IMAGE_SIZE, is_training=True),
        is_training=True
    )
    
    val_dataset = FoodDataset(
        'data/val.csv',
        transform=get_transforms(IMAGE_SIZE, is_training=False),
        is_training=False
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    print(f"📊 Dataset loaded:")
    print(f"  Train: {len(train_dataset)} images")
    print(f"  Val: {len(val_dataset)} images")
    print(f"  Classes: {len(train_dataset.classes)}")
    
    # Create model
    num_classes = len(train_dataset.classes)
    model = FoodRecognitionModel(num_classes=num_classes, pretrained=True)
    
    # Train
    trainer = FoodRecognitionTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        lr=LEARNING_RATE
    )
    
    trainer.train(epochs=EPOCHS)

if __name__ == "__main__":
    main()
