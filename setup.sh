#!/bin/bash
# Setup script for Jetson Nano
# Run with: chmod +x setup.sh && ./setup.sh

set -e  # Exit on error

echo "================================================"
echo "  Touchless Video Controller - Jetson Setup"
echo "================================================"
echo ""

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "⚠️  Warning: This doesn't appear to be a Jetson device"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Updating system packages..."
sudo apt-get update

echo ""
echo "📷 Installing OpenCV..."
sudo apt-get install -y python3-opencv

echo ""
echo "🎬 Installing MPV media player..."
sudo apt-get install -y mpv

echo ""
echo "🔧 Installing Python dependencies..."
sudo apt-get install -y python3-pip python3-dev
sudo pip3 install numpy==1.18.5 h5py==2.10.0 Pillow==8.4.0

echo ""
echo "🤖 Installing TensorFlow for Jetson..."
echo "For JetPack 4.4, run this command manually:"
echo ""
echo "sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v44 tensorflow==2.3.1"
echo ""
read -p "Install TensorFlow now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v44 tensorflow==2.3.1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Transfer these files from your PC:"
echo "   - gesture_model_v1.tflite (rename to gesture_model.tflite)"
echo "   - model_info.json"
echo "   - media_control_mpv.py"
echo ""
echo "2. Start MPV with IPC socket:"
echo "   mpv --input-ipc-server=/tmp/mpv-socket --loop video.mp4 &"
echo ""
echo "3. Run the gesture controller:"
echo "   python3 media_control_mpv.py"
echo ""
echo "================================================"
