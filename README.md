# 🎮 Touchless Video Controller

> Control video playback on NVIDIA Jetson Nano using hand gestures - completely touchless!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.3+](https://img.shields.io/badge/TensorFlow-2.3+-orange.svg)](https://www.tensorflow.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A real-time hand gesture recognition system for touchless media control, optimized for edge deployment on NVIDIA Jetson Nano using TensorFlow Lite.

<p align="center">
  <img src="docs/demo.gif" alt="Demo" width="600"/>
  <br>
  <em>Real-time gesture recognition controlling video playback</em>
</p>

---

## ✨ Features

- 🎯 **5 Gesture Commands**: Play/Pause, Stop, Forward, Reverse, Volume Up
- ⚡ **Real-time Performance**: ~30 FPS on Jetson Nano
- 🚀 **Edge Optimized**: TensorFlow Lite model (8.5 MB)
- 🎬 **MPV Integration**: Direct IPC socket control
- 📊 **High Accuracy**: 96.67% validation accuracy
- 🔄 **Continuous Control**: Hold gestures for volume adjustment
- 🛡️ **Stable Detection**: Requires 0.5s hold time to prevent false triggers
- 💻 **Cross-Platform Training**: Train on PC, deploy to Jetson

---

## 🎮 Gesture Mapping Table

The system includes predefined gestures mapped to specific media player actions.

| Gesture | Description | Media Action | Command |
|---------|-------------|--------------|---------|
| **Play** | Open palm facing camera | Toggle Play       | `cycle play` |
| **Stop** | Closed fist | Pause video | `set pause yes` |
| **Forward** | Left hand thumb pointing right while all fingers are closed | Skip +10 seconds | `seek +10` |
| **Reverse** | Left hand thumb pointing left while all fingers are closed (facing towards user) | Skip -10 seconds | `seek -10` |
| **Volume Up** | Index finger pointing up | Increase volume +10 | `add volume 10` |

---

## 🏗️ Project Structure

```
Touchless-Video-Controller/
├── PC-TRAINING/                    # Training environment (Windows/Linux PC)
│   ├── collect_data.py             # Capture training images
│   ├── train_model.py              # Train MobileNetV2 model
│   ├── create_compatible_tflite.py # Convert to TFLite (Jetson compatible)
│   ├── test_model.py               # Test trained model
│   ├── requirements_pc.txt         # PC dependencies
│   ├── dataset/                    # Training images (5 gesture folders)
│   └── README.md                   # Detailed PC training guide
│
├── JETSON-NANO-PROJECT/            # Deployment (Jetson Nano)
│   ├── media_control_mpv.py        # Real-time gesture control system
│   ├── gesture_model.tflite        # TFLite model (8.5 MB)
│   └── model_info.json             # Model metadata
│
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

**For Training (PC):**
- Python 3.7+
- TensorFlow 2.8+
- Webcam
- Windows/Linux/macOS

**For Deployment (Jetson Nano):**
- NVIDIA Jetson Nano
- JetPack 4.4+ (TensorFlow 2.3.1)
- USB Camera
- MPV Media Player

---

### 📦 Installation

#### 1️⃣ Training on PC

```bash
# Clone the repository
git clone https://github.com/yourusername/Touchless-Video-Controller.git
cd Touchless-Video-Controller/PC-TRAINING

# Install dependencies
pip install -r requirements_pc.txt

# Collect training data (200+ images per gesture, 5 gestures)
python collect_data.py

# Train the model
python train_model.py

# Convert to TensorFlow Lite
python create_compatible_tflite.py
```

**Output:** `gesture_model_v1.tflite` + `model_info.json`

#### 2️⃣ Deployment on Jetson Nano

```bash
# Transfer files to Jetson Nano
scp gesture_model_v1.tflite jetson@192.168.1.x:~/
scp model_info.json jetson@192.168.1.x:~/
scp media_control_mpv.py jetson@192.168.1.x:~/

# SSH into Jetson Nano
ssh jetson@192.168.1.x

# Rename model
mv gesture_model_v1.tflite gesture_model.tflite

# Install dependencies
sudo apt-get update
sudo apt-get install python3-opencv mpv

# Start MPV with IPC socket
mpv --input-ipc-server=/tmp/mpv-socket --loop video.mp4 &

# Run gesture controller
python3 media_control_mpv.py
```

---

## 📖 Usage

### Collecting Training Data

```bash
cd PC-TRAINING
python collect_data.py
```

- Edit `gesture_name` variable in script for each gesture
- Press **A** to toggle auto-capture mode
- Collect **200+ images** per gesture
- Use varied hand positions, angles, and lighting

**Tips:**
- Keep hand centered in green box
- Vary distance from camera (50-100cm)
- Use different lighting conditions
- Include multiple people's hands

### Training the Model

```bash
python train_model.py
```

**Model Architecture:**
- Base: MobileNetV2 (ImageNet pretrained)
- Input: 128×128×3 RGB images
- Output: 5 classes (gestures)
- Optimizer: Adam
- Loss: Categorical Crossentropy

### Converting to TFLite

```bash
python create_compatible_tflite.py
```

Creates two versions:
- `gesture_model_v1.tflite` (8.5 MB) - **Recommended** for Jetson
- `gesture_model_v2.tflite` (2.4 MB) - Optimized (may not work on TF 2.3.1)

### Running on Jetson

```bash
# Terminal 1: Start MPV
mpv --input-ipc-server=/tmp/mpv-socket --loop video.mp4

# Terminal 2: Run gesture controller
python3 media_control_mpv.py
```

**Controls:**
- Show gestures in green box
- Hold for 0.5 seconds at 90%+ confidence
- Press **Q** to quit

---

## 🎯 Performance

| Metric | Value |
|--------|-------|
| **Validation Accuracy** | 96.67% |
| **Inference Speed (Jetson)** | ~25 FPS |
| **Model Size (H5)** | 9.05 MB |
| **Model Size (TFLite)** | 8.48 MB |
| **Latency** | ~33-50 ms |
| **Confidence Threshold** | 90% |
| **Hold Time** | 0.5 seconds |

---

## 🔧 Configuration

Edit parameters in `media_control_mpv.py`:

```python
CONFIDENCE_THRESHOLD = 90.0      # Minimum confidence (%)
GESTURE_HOLD_TIME = 0.5          # Seconds to hold gesture
COMMAND_COOLDOWN = 0.5           # Seconds between repeat commands
VOLUME_CHANGE_INTERVAL = 0.5     # Seconds between volume changes
```

---

## 🛠️ Troubleshooting

### Camera Issues
```bash
# Check available cameras
ls /dev/video*

# Test camera
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### MPV Not Responding
```bash
# Check MPV socket
ls -l /tmp/mpv-socket

# Restart MPV with IPC
pkill mpv
mpv --input-ipc-server=/tmp/mpv-socket --loop video.mp4 &
```

### TFLite Model Errors
- Use `gesture_model_v1.tflite` (not v2)
- Ensure TensorFlow 2.3.1+ is installed
- Verify `model_info.json` has `"class_names"` key

### Low Accuracy
- Collect more training data (200+ per gesture)
- Use diverse lighting and angles
- Retrain model with augmented data
- Ensure consistent gesture definitions

---

## 📚 Documentation

- **[PC-TRAINING/README.md](PC-TRAINING/README.md)** - Complete training guide
- **[PC-TRAINING/QUICK_START.md](PC-TRAINING/QUICK_START.md)** - Quick reference
- **[PC-TRAINING/MPV_SETUP_GUIDE.md](PC-TRAINING/MPV_SETUP_GUIDE.md)** - Jetson setup
- **[PC-TRAINING/DATA_COLLECTION_CHECKLIST.md](PC-TRAINING/DATA_COLLECTION_CHECKLIST.md)** - Data collection tips

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Ideas for Contribution:**
- Add new gesture commands (volume down, brightness, etc.)
- Improve model accuracy
- Add support for other media players (VLC, etc.)
- Create mobile app version
- Add gesture recording/replay

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **TensorFlow Lite** for edge deployment optimization
- **MediaPipe** for hand tracking capabilities
- **MobileNetV2** for efficient image classification
- **NVIDIA Jetson** community for TensorFlow builds
- **MPV Media Player** for IPC socket support

---

## 🗺️ Roadmap

- [x] Basic gesture recognition
- [x] TensorFlow Lite conversion
- [x] MPV integration
- [ ] Add more gestures (brightness, contrast, etc.)
- [ ] VLC player support
- [ ] Real-time hand tracking visualization
- [ ] Web interface for configuration
- [ ] Mobile app version
- [ ] Pre-trained model distribution

---

<p align="center">
  Made with ❤️ for the Edge AI community
</p>
