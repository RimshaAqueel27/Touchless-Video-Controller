#!/bin/bash

echo "========================================"
echo "  Jetson Nano Setup Script"
echo "  Gesture-Based Media Control System"
echo "========================================"
echo ""

# System updates
echo "[1/8] Updating system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Python and build tools
echo "[2/8] Installing Python and build tools..."
sudo apt-get install -y python3-pip python3-dev

# TensorFlow dependencies
echo "[3/8] Installing TensorFlow dependencies..."
sudo apt-get install -y libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran

# OpenCV
echo "[4/8] Installing OpenCV..."
sudo apt-get install -y python3-opencv

# Python packages
echo "[5/8] Installing Python packages..."
sudo pip3 install --upgrade pip
sudo pip3 install numpy==1.18.5
sudo pip3 install h5py==2.10.0
sudo pip3 install Pillow==8.4.0

# TensorFlow for Jetson Nano
echo "[6/8] Installing TensorFlow 2.3.1 for Jetson Nano..."
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v44 tensorflow==2.3.1

# VLC media player
echo "[7/8] Installing VLC media player..."
sudo apt-get install -y vlc

# System optimization
echo "[8/8] Optimizing system for Jetson Nano..."

# Increase swap space
sudo systemctl disable nvzramconfig
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Set performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

echo ""
echo "========================================"
echo "  Verifying Installation"
echo "========================================"
python3 -c "import tensorflow as tf; print('TensorFlow:', tf.__version__); print('GPU:', tf.config.list_physical_devices('GPU'))"
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"
python3 -c "import numpy; print('NumPy:', numpy.__version__)"

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo "To run the media control system:"
echo "  python3 media_control.py"
echo ""
