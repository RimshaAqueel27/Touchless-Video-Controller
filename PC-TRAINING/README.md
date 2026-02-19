# 🎮 Jetson Nano Gesture-Based MPV Control

**Control MPV media player on NVIDIA Jetson Nano using hand gestures - completely touchless!**

> 🚀 **Project Status:** Data Collection Phase (33% complete)  
> 📋 **See:** [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed current status

---

## 🎯 What This Does

Control MPV video playback with hand gestures:
- **Play/Pause** - Toggle playback
- **Stop** - Stop video
- **Forward/Reverse** - Skip ±10 seconds
- **Volume Up/Down** - Continuous volume control (hold gesture to keep changing)

---

## ⚡ Quick Start

### 1️⃣ Collect Training Data (ON PC)
```bash
python collect_data.py
```
- Edit `gesture_name` in script for each gesture
- Press **A** to toggle auto-capture
- Collect **200+ images** per gesture
- **See:** [DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md)

### 2️⃣ Train Model (ON PC)
```bash
python train_model.py                 # Train MobileNetV2 model
python create_compatible_tflite.py    # Convert to TFLite
```

### 3️⃣ Deploy to Jetson Nano
```bash
# Transfer 3 files:
gesture_model_v1.tflite → gesture_model.tflite
model_info.json
media_control_mpv.py
```
**See:** [MPV_SETUP_GUIDE.md](MPV_SETUP_GUIDE.md) for complete installation guide

### 4️⃣ Run on Jetson
```bash
# Terminal 1: Start MPV
mpv --loop video.mp4

# Terminal 2: Run gesture control
python3 media_control_mpv.py
```

---

## 📋 Project Files

### 🔥 Core Scripts
| File | Purpose | Status |
|------|---------|--------|
| [collect_data.py](collect_data.py) | Collect training images with progress tracker | ✅ Ready |
| [train_model.py](train_model.py) | Train MobileNetV2 gesture classifier | ✅ Ready |
| [create_compatible_tflite.py](create_compatible_tflite.py) | Convert to TensorFlow Lite (Jetson compatible) | ✅ Ready |
| [media_control_mpv.py](media_control_mpv.py) | Real-time MPV control via gestures | ✅ Ready |

### 📦 Model Files
| File | Size | Description |
|------|------|-------------|
| gesture_model_v1.tflite | 8.48 MB | ✅ Use this for Jetson (TF 2.3.1 compatible) |
| gesture_model_v2.tflite | 2.40 MB | ⚠️ Optimized (may not work on TF 2.3.1) |
| model_info.json | - | 📋 Class names (required) |
| ~~gesture_model.h5~~ | 9.05 MB | ❌ Don't use (incompatible with Jetson) |

### 📁 Dataset Status
```
dataset/
├── play/         ✅ 200+ images  
├── stop/         ✅ 200+ images
├── forward/      ⚠️  80 images (need 120+ more)
├── reverse/      ❌ Empty (need 200+)
└── volume_up/    ❌ Empty (need 200+)
```

### 📄 Documentation
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Complete project status and workflow
- **[MPV_SETUP_GUIDE.md](MPV_SETUP_GUIDE.md)** - Jetson installation and usage guide
- **[DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md)** - Collection progress and tips
- **TFLITE_SOLUTION.txt** - Technical details on TFLite conversion
- **FIX_SUMMARY.txt** - Compatibility issue resolutions

---

## 🎮 Gesture Mappings

| Gesture | MPV Command | Behavior |
|---------|-------------|----------|
| **play** | `playerctl play-pause` | Toggle play/pause |
| **stop** | `playerctl stop` | Stop playback |
| **forward** | `playerctl position 10+` | Skip forward 10 seconds |
| **reverse** | `playerctl position 10-` | Skip backward 10 seconds |
| **volume_up** | `pactl +5%` (every 0.3s) | Continuous increase while held |

---

## 🔧 System Requirements

### Training (PC - Windows)
- Python 3.x
- TensorFlow 2.20.0
- OpenCV
- Webcam

### Deployment (Jetson Nano - Linux)
- Python 3.6.9
- TensorFlow 2.3.1 (NVIDIA build)
- OpenCV
- MPV, playerctl, pulseaudio-utils
- USB/CSI Camera

---

## 📊 Model Details

- **Architecture:** MobileNetV2 (ImageNet pretrained) + custom classifier
- **Input:** 128x128x3 RGB images
- **Output:** 6 gesture classes
- **Format:** TensorFlow Lite (edge optimized)
- **Performance:** 96.67% validation accuracy (with partial dataset)
- **Inference:** ~30 FPS on Jetson Nano

---

## 🚨 Current Status & Next Steps

### ⚠️ ACTION REQUIRED
**You need to collect more training data before deployment!**

**Next Steps:**
1. ✅ **Start data collection** - Use collect_data.py for remaining gestures
2. ⏳ Retrain model with complete dataset
3. ⏳ Transfer files to Jetson Nano
4. ⏳ Test MPV control on Jetson

**See [DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md) for detailed instructions.**

---

## 💡 Key Features

- ✅ **Continuous Volume Control** - Hold gesture to keep changing volume
- ✅ **Gesture Stability Check** - Requires 3 consecutive frames (reduces false triggers)
- ✅ **Progress Tracker** - Visual feedback during data collection
- ✅ **TFLite Optimized** - Compatible with TensorFlow 2.3.1 on Jetson
- ✅ **MPV Integration** - Uses playerctl for smooth media control
- ✅ **Real-time Feedback** - On-screen status and confidence display

---

## 🐛 Troubleshooting

**Camera not opening?**
```bash
ls /dev/video*  # Check available cameras
```

**MPV not responding?**
```bash
playerctl -l  # Should show: mpv
sudo apt-get install playerctl  # Install if missing
```

**Model loading error on Jetson?**
- Use `gesture_model_v1.tflite` (not v2 or .h5)
- Ensure `model_info.json` is in same directory

**Low gesture accuracy?**
- Collect more training images (target: 200+ per gesture)
- Retrain model after data collection
- Ensure good lighting during testing

---

## 📖 Detailed Documentation

For complete instructions, see:
- **Getting Started:** [MPV_SETUP_GUIDE.md](MPV_SETUP_GUIDE.md)
- **Data Collection:** [DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md)
- **Full Project Status:** [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

## 🔥 Why TensorFlow Lite?

The H5 model trained on PC (TF 2.20) is **incompatible** with Jetson Nano (TF 2.3.1). TensorFlow Lite solves this:
- ✅ Cross-version compatible
- ✅ Optimized for edge devices
- ✅ Faster inference on Jetson
- ✅ Smaller model size (2.40 MB vs 9.05 MB)

---

## 📄 License

MIT License

## 👨‍💻 Author

Jetson Nano Gesture Control Project - 2026

---

**📌 Start here:** [DATA_COLLECTION_CHECKLIST.md](DATA_COLLECTION_CHECKLIST.md) - Begin collecting training data!
