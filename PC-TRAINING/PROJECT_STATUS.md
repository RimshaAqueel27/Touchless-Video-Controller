# 🎮 Jetson Nano Gesture Control Project - Current Status

**Last Updated:** February 19, 2026  
**Project:** Touchless MPV Media Control via Hand Gestures  
**Platform:** PC (Training) → Jetson Nano (Deployment)

---

## 📌 Project Overview

Control MPV media player on Jetson Nano using hand gestures captured by camera:
- **5 Gestures:** play, stop, forward, reverse, volume_up
- **Model:** MobileNetV2 (pretrained) + custom classifier
- **Deployment:** TensorFlow Lite (compatible with TF 2.3.1 on Jetson)
- **Media Control:** MPV via IPC socket
- **Features:** Continuous volume control, 0.5s gesture hold time, 90% confidence threshold

---

## 🔥 CURRENT STATUS

### ⚠️ ACTION REQUIRED: Data Collection
**You need to collect more training images before deploying!**

| Priority | Gesture | Status | Action |
|----------|---------|--------|--------|
| 🔴 HIGH | **forward** | 80/200 images | Need 120+ more |
| 🔴 HIGH | **reverse** | 0/200 images | Need 200+ |
| 🟡 MEDIUM | **volume_up** | 0/200 images | Need 200+ |
| ✅ DONE | play | 200+ images | Ready |
| ✅ DONE | stop | 200+ images | Ready |

**See:** [DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md) for detailed instructions

---

## 📂 Project Files

### 🎯 Core Python Scripts

#### 1. collect_data.py ✅ READY
**Purpose:** Collect training images with progress tracking  
**Features:**
- Visual progress tracker for all 6 gestures
- Color-coded status (green/yellow/red)
- Target: 200+ images per gesture
- Auto-capture mode (1 image/0.3s)
- Session summary on quit

**Usage:**
```python
# Edit line to change gesture:
gesture_name = "forward"  # or: reverse, volume_up

# Run:
python collect_data.py
```

#### 2. train_model.py ✅ READY
**Purpose:** Train MobileNetV2-based gesture classifier  
**Features:**
- Auto-detects classes from dataset/ folder
- MobileNetV2 (ImageNet weights) + custom top layer
- Batch size 8 (optimized for Jetson)
- Output: gesture_model.h5

**Current Performance (with partial dataset):**
- Training accuracy: 100%
- Validation accuracy: 96.67%
- Total images: 460

**Usage:**
```bash
python train_model.py
```

#### 3. create_compatible_tflite.py ✅ READY
**Purpose:** Convert H5 model to TensorFlow Lite  
**Features:**
- Creates 2 versions (v1: compatible, v2: optimized)
- v1: 8.48MB (TFLITE_BUILTINS only - use this for Jetson!)
- v2: 2.40MB (optimized with SELECT_TF_OPS)
- Outputs model_info.json with class names

**Usage:**
```bash
python create_compatible_tflite.py
```

#### 4. media_control_mpv.py ✅ READY
**Purpose:** Real-time gesture recognition and MPV control  
**Features:**
- TFLite interpreter (edge optimized)
- Continuous volume control (hold gesture)
- 3-frame gesture stability check
- Platform detection (Jetson vs Windows)
- On-screen status display

**Gesture Mappings:**
| Gesture | Command | Effect |
|---------|---------|--------|
| play | `playerctl play-pause` | Toggle playback |
| stop | `playerctl stop` | Stop video |
| forward | `playerctl position 10+` | Skip +10s |
| reverse | `playerctl position 10-` | Skip -10s |
| volume_up | `pactl +5%` (every 0.3s) | Continuous increase |

**Usage (on Jetson):**
```bash
# Terminal 1: Start MPV first
mpv --loop video.mp4

# Terminal 2: Run gesture control
python3 media_control_mpv.py
```

---

### 📦 Model Files

#### gesture_model.h5 ⚠️ OUTDATED
- Size: 9.05 MB
- Status: Original H5 model (incompatible with Jetson TF 2.3.1)
- **Do not transfer to Jetson!**

#### gesture_model_v1.tflite ✅ USE THIS
- Size: 8.48 MB
- Status: Compatible TFLite (TFLITE_BUILTINS only)
- **Transfer this to Jetson as `gesture_model.tflite`**

#### gesture_model_v2.tflite ⚠️ TESTING
- Size: 2.40 MB (73.5% smaller)
- Status: Optimized TFLite (may not work on TF 2.3.1)
- Try v1 first, use v2 if v1 has issues

#### model_info.json ✅ REQUIRED
- Contains: Class names in correct order
- **Must transfer with TFLite model**

---

### 📁 Dataset Folder

```
dataset/
├── forward/        ⚠️ 80 images (need 120+ more)
├── play/           ✅ 200+ images
├── reverse/        ❌ Empty (need 200+)
├── stop/           ✅ 200+ images
└── volume_up/      ❌ Empty (need 200+)
```

---

### 📄 Documentation Files

1. **MPV_SETUP_GUIDE.md** - Complete installation and usage guide for Jetson
2. **DATA_COLLECTION_CHECKLIST.md** - Data collection progress and instructions
3. **TFLITE_SOLUTION.txt** - Technical details on TFLite conversion
4. **FIX_SUMMARY.txt** - Compatibility issues and solutions
5. **TRANSFER_GUIDE.md** - File transfer instructions

---

## 🔄 Complete Workflow

### Phase 1: Data Collection (CURRENT PHASE) ⏳
```bash
cd d:\Jetson-Nano-project\New_PROJECT

# Collect images for each gesture (edit gesture_name in script)
python collect_data.py
```
**Status:** 2/6 gestures complete  
**Next:** Collect for forward, reverse, volume_up, volume_down

---

### Phase 2: Model Training 🔜
```bash
# After collecting all images
python train_model.py           # Creates gesture_model.h5
python create_compatible_tflite.py  # Creates .tflite + model_info.json
```
**Expected:** Better accuracy with complete dataset (target: 95%+)

---

### Phase 3: Transfer to Jetson 🔜
**Files to copy:**
```
gesture_model_v1.tflite  → gesture_model.tflite
model_info.json
media_control_mpv.py
```

**Transfer method:** USB drive or SCP:
```bash
scp gesture_model_v1.tflite ris@jetson:~/Downloads/New_PROJECT/New_PROJECT/gesture_model.tflite
scp model_info.json ris@jetson:~/Downloads/New_PROJECT/New_PROJECT/
scp media_control_mpv.py ris@jetson:~/Downloads/New_PROJECT/New_PROJECT/
```

---

### Phase 4: Jetson Deployment 🔜
```bash
# Install dependencies (first time only)
sudo apt-get install mpv playerctl pulseaudio-utils

# Terminal 1: Start MPV
mpv --loop ~/Videos/test.mp4

# Terminal 2: Run gesture control
cd ~/Downloads/New_PROJECT/New_PROJECT
python3 media_control_mpv.py
```

---

## 🛠️ Technical Specifications

### PC (Training Environment)
- OS: Windows
- Python: 3.x (with TensorFlow 2.20.0)
- Purpose: Data collection, model training, TFLite conversion

### Jetson Nano (Deployment Environment)
- OS: Linux (Ubuntu 18.04)
- Python: 3.6.9
- TensorFlow: 2.3.1 (NVIDIA build for ARM)
- Camera: USB/CSI camera (640x480)

### Model Details
- **Base:** MobileNetV2 (ImageNet pretrained)
- **Top Layer:** GlobalAveragePooling2D → Dense(6, softmax)
- **Input:** 224x224x3 RGB images
- **Output:** 6 classes (play, stop, forward, reverse, volume_up, volume_down)
- **Inference:** TensorFlow Lite interpreter

### Performance Settings
- **Batch Size:** 8 (Jetson memory optimized)
- **Confidence Threshold:** 75%
- **Gesture Stability:** 3 consecutive frames
- **Volume Interval:** 0.3 seconds (continuous control)
- **Command Cooldown:** 1.5 seconds (non-volume gestures)

---

## 🚨 Known Issues & Solutions

### ❌ Issue 1: H5 Model Incompatibility
**Problem:** TensorFlow 2.20 (PC) → 2.3.1 (Jetson) H5 format mismatch  
**Solution:** ✅ Use TFLite format instead (gesture_model_v1.tflite)

### ❌ Issue 2: CONV_2D Version Error
**Problem:** Optimized TFLite ops not in TF 2.3.1  
**Solution:** ✅ Created v1 with TFLITE_BUILTINS only (no optimization)

### ❌ Issue 3: Low Forward Gesture Accuracy
**Problem:** Only 80 images collected for forward  
**Solution:** ⏳ Collect 120+ more images (in progress)

### ❌ Issue 4: Missing Volume Gestures
**Problem:** No data for reverse/volume_up/volume_down  
**Solution:** ⏳ Collect 200+ images each (in progress)

---

## 📊 Success Metrics

### Training Metrics (Target)
- [x] Validation accuracy > 95% ✅ (currently 96.67% with partial data)
- [ ] All gesture classes balanced (200+ images each) ⏳ (2/6 complete)
- [ ] Low false positive rate on testing ⏳ (pending full training)

### Deployment Metrics (Target)
- [ ] Gesture response time < 0.5s ⏳
- [ ] Accurate recognition in varied lighting ⏳
- [ ] Continuous volume control works smoothly ⏳
- [ ] No MPV control conflicts with manual input ⏳

---

## 🎯 Immediate Next Steps

### 1. Complete Data Collection (HIGH PRIORITY)
```bash
python collect_data.py
```
- [ ] Collect 120+ more forward images
- [ ] Collect 200+ reverse images  
- [ ] Collect 200+ volume_up images


**Estimated time:** 50-60 minutes total

### 2. Retrain Model
```bash
python train_model.py
python create_compatible_tflite.py
```

### 3. Transfer to Jetson
- Copy gesture_model_v1.tflite → gesture_model.tflite
- Copy model_info.json
- Copy media_control_mpv.py

### 4. Test on Jetson
- Start MPV with test video
- Run gesture control
- Verify all 6 gestures work correctly

---

## 📞 Quick Reference

### Keyboard Controls (collect_data.py)
- **Space** - Capture image
- **A** - Toggle auto-capture
- **Q** - Quit with summary

### Terminal Commands (Jetson)
```bash
# Check MPV status
playerctl -p mpv status

# Manual MPV control
playerctl -p mpv play-pause
playerctl -p mpv position 10+

# Check camera
ls /dev/video*
```

---

## 📈 Version History

- **v1.0** - Initial H5 model (96.67% accuracy, partial dataset)
- **v1.1** - TFLite conversion with compatibility fixes
- **v1.2** - MPV integration with continuous volume control (CURRENT)
- **v2.0** - Complete dataset retraining (PENDING data collection)

---

**Current Phase:** Data Collection (33% complete)  
**Blocking Issue:** Need to collect images for 4 remaining gestures  
**Next Milestone:** Complete dataset → Retrain → Deploy to Jetson

**Status:** ⚠️ Ready for data collection, NOT ready for Jetson deployment yet

---

For detailed guides, see:
- [MPV_SETUP_GUIDE.md](MPV_SETUP_GUIDE.md) - Jetson installation and usage
- [DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md) - Collection progress and tips
