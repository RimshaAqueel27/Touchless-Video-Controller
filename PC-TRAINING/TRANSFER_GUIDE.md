# Transfer Guide: PC to Jetson Nano

## ✅ Files Ready for Transfer

The following files have been created and are compatible with Jetson Nano's TensorFlow 2.3.1:

### Essential Files (MUST transfer):
1. **gesture_model_jetson.h5** (9.19 MB) - Compatible model ⭐
2. **media_control.py** - Updated with compatibility fallback
3. **class_names.txt** - Gesture class names
4. **dataset/** folder - For class name lookup

### Backup Files (optional but recommended):
5. **gesture_model.weights.h5** - Model weights only
6. **model_architecture.json** - Model architecture
7. **test_model.py** - Updated test script

---

## 📦 Method 1: USB Transfer (Easiest)

```bash
# On PC - Copy to USB drive
# Copy these files from: d:\Jetson-Nano-project\New_PROJECT\

gesture_model_jetson.h5
media_control.py
class_names.txt
dataset/ (entire folder)

# On Jetson Nano - Copy from USB to home directory
cd ~/Downloads/New_PROJECT
cp /media/YOUR_USB_NAME/gesture_model_jetson.h5 .
cp /media/YOUR_USB_NAME/media_control.py .
cp /media/YOUR_USB_NAME/class_names.txt .
```

---

## 🌐 Method 2: SCP Transfer (Over Network)

```bash
# On PC PowerShell (from d:\Jetson-Nano-project\New_PROJECT\)
scp gesture_model_jetson.h5 ris@JETSON_IP:~/Downloads/New_PROJECT/
scp media_control.py ris@JETSON_IP:~/Downloads/New_PROJECT/
scp class_names.txt ris@JETSON_IP:~/Downloads/New_PROJECT/
scp test_model.py ris@JETSON_IP:~/Downloads/New_PROJECT/

# Or copy all at once:
scp gesture_model_jetson.h5 media_control.py class_names.txt test_model.py ris@JETSON_IP:~/Downloads/New_PROJECT/
```

---

## ✅ Verify on Jetson Nano

```bash
cd ~/Downloads/New_PROJECT
ls -lh

# You should see:
# gesture_model_jetson.h5  (~9.2 MB)
# media_control.py
# class_names.txt
# dataset/ (folder)
```

---

## 🚀 Run on Jetson Nano

```bash
cd ~/Downloads/New_PROJECT
python3 media_control.py
```

### Expected Output:
```
Loading gesture_model_jetson.h5...
✓ Model loaded successfully
Loaded classes from file: ['forward', 'play', 'reverse', 'stop', 'volume_down', 'volume_up']
==================================================
GESTURE-BASED MEDIA CONTROL SYSTEM
==================================================
Confidence Threshold: 75.0%
Cooldown Time: 2.0s

Gesture Mappings:
  play       → Play/Pause
  stop       → Stop
  forward    → Next Track
  reverse    → Previous Track
  volume_up  → Increase Volume
  volume_down→ Decrease Volume

Press 'q' to quit
==================================================
```

---

## 🐛 If You Still Get Errors

### Error: "Could not load model"
```bash
# Check file exists
ls -lh gesture_model_jetson.h5

# If missing, retransfer from PC
```

### Error: "No module named tensorflow"
```bash
# Verify TensorFlow installation
python3 -c "import tensorflow as tf; print(tf.__version__)"
```

### Error: Still getting compatibility errors
```bash
# Use the backup method - load from architecture + weights
# The code will automatically try this if H5 loading fails
```

---

## 📝 Quick Commands Summary

```bash
# On Jetson Nano once files are transferred:
cd ~/Downloads/New_PROJECT
ls -lh gesture_model_jetson.h5  # Verify file exists
python3 media_control.py         # Run the application
# Press 'q' to quit
```

---

**Status**: ✅ Ready for transfer
**Compatibility**: TensorFlow 2.3.1 (Jetson Nano)
**Date**: February 15, 2026
