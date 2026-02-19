# MPV Setup and Installation Guide for Jetson Nano

## 📦 Installation on Jetson Nano

### 1. Install MPV Media Player
```bash
sudo apt-get update
sudo apt-get install mpv
```

### 2. Install playerctl (for gesture control)
```bash
sudo apt-get install playerctl
```

### 3. Install PulseAudio Control (for volume)
```bash
sudo apt-get install pulseaudio-utils
```

### 4. Verify Installation
```bash
mpv --version
playerctl --version
pactl --version
```

---

## 🚀 Running the Project

### Step 1: Start MPV with a Video
```bash
# Basic usage
mpv --idle --force-window /path/to/your/video.mp4

# Loop video continuously
mpv --loop /path/to/your/video.mp4

# With fullscreen
mpv --fs /path/to/your/video.mp4

# Example with test video
mpv --loop ~/Videos/test.mp4
```

**Important:** MPV must be running BEFORE starting gesture control!

### Step 2: Run Gesture Control (in another terminal)
```bash
cd ~/Downloads/New_PROJECT/New_PROJECT
python3 media_control_mpv.py
```

---

## 🎮 Gesture Controls

| Gesture | Action | Notes |
|---------|--------|-------|
| **play** | Play/Pause | Toggle playback |
| **stop** | Stop | Stop playback |
| **forward** | Skip +10s | Jump forward in video |
| **reverse** | Skip -10s | Jump backward in video |
| **volume_up** | Volume +5% | Hold for continuous increase |

---

## 📊 Data Collection Status

### Required: 200+ images per gesture

**Before training, collect data for these gestures:**

```bash
cd ~/Downloads/New_PROJECT
python collect_data.py
```

**Change `gesture_name` in collect_data.py for each gesture:**
1. **forward** - ⚠️ Needs more (target: 200+)
2. **play** - ✓ Complete
3. **reverse** - ✗ Not collected (target: 200+)
4. **stop** - ✓ Complete  
5. **volume_up** - ✗ Not collected (target: 200+)

---

## 🔧 Troubleshooting

### MPV not responding to gestures
```bash
# Check if MPV is running
playerctl -l

# Should show: mpv

# Test manual control
playerctl -p mpv play-pause
playerctl -p mpv position 10+
```

### playerctl not found
```bash
sudo apt-get install playerctl
```

### Volume control not working
```bash
# Check PulseAudio
pactl info

# Test manual volume
pactl set-sink-volume @DEFAULT_SINK@ +5%
pactl set-sink-volume @DEFAULT_SINK@ -5%
```

### Camera not opening
```bash
# Check available cameras
ls /dev/video*

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

---

## 📝 Complete Workflow

### On PC (Training):
```bash
cd d:\Jetson-Nano-project\New_PROJECT

# 1. Collect data (200+ images per gesture)
#    Edit gesture_name in collect_data.py for each gesture
python collect_data.py

# 2. Train model
python train_model.py

# 3. Convert to TFLite (compatible version)
python create_compatible_tflite.py
```

### Transfer to Jetson Nano:
```
gesture_model_v1.tflite  → gesture_model.tflite
model_info.json
media_control_mpv.py
```

### On Jetson Nano (Deployment):
```bash
cd ~/Downloads/New_PROJECT/New_PROJECT

# 1. Rename TFLite model
mv gesture_model_v1.tflite gesture_model.tflite

# 2. Start MPV with video (Terminal 1)
mpv --loop ~/Videos/your_video.mp4

# 3. Run gesture control (Terminal 2)
python3 media_control_mpv.py
```

---

## ⚙️ MPV Advanced Options

### Start MPV on boot (optional)
```bash
# Create systemd service
sudo nano /etc/systemd/system/mpv-autostart.service
```

Add:
```ini
[Unit]
Description=MPV Media Player
After=graphical.target

[Service]
Type=simple
User=ris
Environment=DISPLAY=:0
ExecStart=/usr/bin/mpv --loop --fs /home/ris/Videos/demo.mp4
Restart=always

[Install]
WantedBy=graphical.target
```

Enable:
```bash
sudo systemctl enable mpv-autostart
sudo systemctl start mpv-autostart
```

---

## 🎯 Performance Tips

1. **Reduce Latency:**
   - Use `--cache=no` in MPV for faster response
   - Disable unnecessary MPV features

2. **Optimize for Jetson:**
   - Close unnecessary applications
   - Enable performance mode: `sudo jetson_clocks`
   - Use hardware acceleration: `--hwdec=auto`

3. **Best Practice:**
   - Test in controlled lighting first
   - Keep hand within ROI box clearly
   - Hold gestures steady for 3 frames

---

## 📱 Quick Commands Reference

```bash
# Start MPV
mpv --loop video.mp4

# Check MPV status
playerctl -p mpv status

# Control MPV manually
playerctl -p mpv play-pause
playerctl -p mpv stop
playerctl -p mpv position 10+
playerctl -p mpv position 10-

# Volume control
pactl set-sink-volume @DEFAULT_SINK@ +5%
pactl set-sink-volume @DEFAULT_SINK@ -5%

# Check camera
ls /dev/video*
v4l2-ctl --list-devices
```

---

**Status:** Ready for Deployment ✅  
**Date:** February 15, 2026
