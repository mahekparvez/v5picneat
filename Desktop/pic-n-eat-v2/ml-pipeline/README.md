# Pic N Eat V2 - ML Training Pipeline

Custom food classification model trained on WWEIA (What We Eat In America) dataset.

## Dataset Setup

### 1. Download WWEIA Dataset

The WWEIA database contains food images and nutrition data from USDA.

**Dataset URL:** https://agdatacommons.nal.usda.gov/articles/dataset/What_We_Eat_In_America_WWEIA_Database/24660126

```bash
# Download the dataset
wget https://agdatacommons.nal.usda.gov/articles/dataset/What_We_Eat_In_America_WWEIA_Database/24660126/files/latest/download -O wweia_dataset.zip

# Extract
unzip wweia_dataset.zip -d data/raw/

# Expected structure:
# data/raw/
#   ├── food_images/
#   │   ├── breakfast/
#   │   ├── lunch/
#   │   ├── dinner/
#   │   └── snacks/
#   ├── food_codes.csv
#   └── nutrition_mapping.csv
```

### 2. Process Dataset

Our preprocessing script will:
- Map WWEIA food codes to USDA FDC IDs
- Organize images by food category
- Create train/val/test splits (80/10/10)
- Generate class labels

```bash
python scripts/preprocess_dataset.py
```

This creates:
```
data/processed/
  ├── train/
  ├── val/
  ├── test/
  ├── class_names.json
  └── fdc_mapping.json
```

## Model Architecture

We use **EfficientNet-B3** as the base model (better than MobileNetV2 for production):

```
EfficientNet-B3 (pretrained on ImageNet)
    ├── Feature extraction: 1536 features
    ├── Global average pooling
    ├── Dropout (0.3)
    └── Classification head: 1000+ food classes
```

**Why EfficientNet-B3?**
- Better accuracy than MobileNet for similar inference speed
- Compound scaling (depth + width + resolution)
- ~12M parameters vs MobileNetV2's 3.5M
- Target: >85% Top-1 accuracy

## Training

### Requirements
```bash
pip install -r requirements.txt
```

### Train Model

```bash
# Train with default config
python scripts/train.py

# Train with custom config
python scripts/train.py --config configs/efficientnet_b3.yaml
```

### Training Config

Key hyperparameters (in `configs/efficientnet_b3.yaml`):
```yaml
model:
  architecture: efficientnet_b3
  num_classes: 1000  # Automatically detected from dataset
  pretrained: true

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
  optimizer: adamw
  scheduler: cosine
  early_stopping_patience: 10

augmentation:
  random_crop: true
  horizontal_flip: true
  color_jitter: true
  rotation: 15
```

## Data Augmentation

Heavy augmentation to prevent overfitting:

```python
train_transforms = A.Compose([
    A.RandomResizedCrop(224, 224),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.3),
    A.ColorJitter(p=0.3),
    A.Rotate(limit=15, p=0.3),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])
```

## Evaluation

```bash
# Evaluate on test set
python scripts/evaluate.py --checkpoint models/best_model.pth

# Metrics:
# - Top-1 Accuracy
# - Top-5 Accuracy
# - Per-class F1 scores
# - Confusion matrix
```

Expected results:
- Top-1 Accuracy: >85%
- Top-5 Accuracy: >95%
- Inference time: ~30ms on CPU, ~5ms on GPU

## Export for Production

Convert PyTorch model to ONNX for faster inference:

```bash
python scripts/export_onnx.py --checkpoint models/best_model.pth

# Creates: models/food_classifier.onnx
# Optimized for CPU inference with quantization
```

## Model Files

```
models/
  ├── best_model.pth          # Full PyTorch checkpoint
  ├── food_classifier.pth     # Production model (state_dict only)
  ├── food_classifier.onnx    # ONNX export
  ├── class_names.json        # Food class labels
  └── training_metrics.json   # Training history
```

## Portion Estimation

Portion size estimation is still under development. Current approaches:

1. **Reference object detection** (coins, hands, plates)
2. **Depth estimation** from monocular images
3. **Known food size database** (e.g., banana ≈ 118g)

For now, we use average portions per food type.

## Integration with Backend

Once trained, copy model to backend:

```bash
cp models/food_classifier.pth ../backend/models/
```

Backend will load it automatically using the ML service.

## Training Monitoring

We use Weights & Biases for experiment tracking:

```bash
# Login to W&B
wandb login

# Training will automatically log:
# - Loss curves
# - Accuracy metrics
# - Learning rate schedule
# - Sample predictions
```

## Troubleshooting

**Out of memory during training:**
- Reduce batch_size in config
- Use mixed precision training (automatically enabled)
- Reduce image size to 192x192

**Low accuracy:**
- Increase training epochs
- Adjust learning rate
- Check data quality (corrupted images)
- Verify class balance

**Slow inference:**
- Export to ONNX
- Enable quantization
- Use GPU if available

## Next Steps

1. Download WWEIA dataset
2. Run preprocessing script
3. Train model with default config
4. Evaluate on test set
5. Export to production format
6. Copy to backend/models/
