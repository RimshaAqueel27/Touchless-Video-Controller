# Gesture-Based Media Control System
# Quick Start Guide

## For PC (Training)

### 1. Install Dependencies
```bash
pip install -r requirements_pc.txt
```

### 2. Collect Data
```bash
python collect_data.py
```
Edit `gesture_name` variable for each gesture, collect 100-150 images per gesture.

### 3. Train Model
```bash
python train_model.py
```
This creates `gesture_model.h5`

### 4. Convert to TFLite
```bash
python create_compatible_tflite.py
```
This creates `gesture_model_v1.tflite` and `model_info.json`

### 5. Test Model
```bash
python test_model.py
```

## For Jetson Nano (Deployment)

### 1. Transfer Files
Copy these files to Jetson Nano:
- `gesture_model_v1.tflite` (rename to `gesture_model.tflite`)
- `model_info.json`
- `media_control_mpv.py`

### 2. Setup Jetson Nano (one-time)
```bash
chmod +x setup_jetson.sh
./setup_jetson.sh
```

### 3. Run Media Control
```bash
python3 media_control_mpv.py
```

## Gesture Commands
- **play**: Play/Pause toggle
- **stop**: Pause
- **forward**: +10 seconds
- **reverse**: -10 seconds
- **volume_up**: Volume +10%

## Configuration
Edit `media_control.py`:
- `CONFIDENCE_THRESHOLD = 90.0` - Minimum confidence (0-100)
- `COOLDOWN_TIME = 0.5` - Seconds between commands

Press 'q' to quit the application.
