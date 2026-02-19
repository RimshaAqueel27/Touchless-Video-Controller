"""
Real-time Gesture Recognition for MPV Media Control
Uses TensorFlow Lite model for edge deployment on Jetson Nano
Controls MPV via IPC socket (no external packages needed!)
"""
import cv2
import numpy as np
import tensorflow as tf
import json
import os
import time
import platform
import subprocess
import socket

# Configuration
MODEL_PATH = 'gesture_model.tflite'
MODEL_INFO_PATH = 'model_info.json'
MPV_SOCKET = '/tmp/mpv-socket'
CONFIDENCE_THRESHOLD = 90.0  # 90%+ confidence required
COMMAND_COOLDOWN = 0.5  # seconds between commands (for forward/reverse)
VOLUME_CHANGE_INTERVAL = 0.5  # 0.5 seconds between volume changes
GESTURE_HOLD_TIME = 0.5  # Must hold gesture for 0.5 seconds before triggering

# Detect platform
IS_JETSON = os.path.exists('/etc/nv_tegra_release') or 'tegra' in platform.platform().lower()
PLATFORM_NAME = "Jetson Nano" if IS_JETSON else "Windows (Simulation)"

print("=" * 50)
print("MPV Gesture Control (TFLite)")
print("=" * 50)

# Load TFLite model
if not os.path.exists(MODEL_PATH):
    print(f"\n❌ ERROR: Model file not found: {MODEL_PATH}")
    print("Please ensure gesture_model.tflite is in the same directory.")
    exit(1)

print(f"\nLoading model: {MODEL_PATH}")
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']
IMG_SIZE = input_shape[1]

print(f"✓ Model loaded successfully")
print(f"  Input shape: {input_shape}")
print(f"  Image size: {IMG_SIZE}x{IMG_SIZE}")

# Load class names
if os.path.exists(MODEL_INFO_PATH):
    with open(MODEL_INFO_PATH, 'r') as f:
        model_info = json.load(f)
        class_names = model_info['class_names']
    print(f"✓ Loaded class names from {MODEL_INFO_PATH}")
else:
    # Fallback to directory listing
    dataset_path = 'dataset'
    if os.path.exists(dataset_path):
        class_names = sorted([d for d in os.listdir(dataset_path) 
                            if os.path.isdir(os.path.join(dataset_path, d))])
        print(f"⚠ Using class names from dataset folder")
    else:
        class_names = ['forward', 'play', 'reverse', 'stop', 'volume_up']
        print(f"⚠ Using default class names")

print(f"  Classes: {class_names}")
print(f"  Platform: {PLATFORM_NAME}")
if IS_JETSON:
    print(f"  MPV Socket: {MPV_SOCKET}")
    print("\n⚠ IMPORTANT: Start MPV with IPC socket:")
    print("  mpv --input-ipc-server=/tmp/mpv-socket --loop video.mp4")
print("\nPress 'q' to quit")
print("=" * 50 + "\n")

# MPV command mappings (JSON IPC format)
MPV_COMMANDS = {
    'play': {'command': ['cycle', 'pause']},
    'stop': {'command': ['cycle', 'pause']},  # Pause instead of stop
    'forward': {'command': ['seek', '10']},   # Skip forward 10 seconds
    'reverse': {'command': ['seek', '-10']},  # Skip backward 10 seconds
    'volume_up': {'command': ['add', 'volume', '10']}     # Increase volume by 10%
}

def send_mpv_command(gesture):
    """Send command to MPV via IPC socket"""
    if gesture not in MPV_COMMANDS:
        return False
    
    if IS_JETSON:
        sock = None
        try:
            # Connect to MPV socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(MPV_SOCKET)
            
            # Send JSON command
            command = json.dumps(MPV_COMMANDS[gesture]) + '\n'
            sock.sendall(command.encode('utf-8'))
            
            # Read response to avoid broken pipe
            try:
                sock.recv(1024)
            except:
                pass
            
            return True
        except (socket.error, FileNotFoundError, ConnectionRefusedError, OSError):
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    else:
        # Simulation mode on Windows
        print(f"  [SIMULATION] Would send: {MPV_COMMANDS[gesture]}")
        return True

def check_mpv_status():
    """Check if MPV IPC socket is available"""
    if IS_JETSON:
        sock = None
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(MPV_SOCKET)
            return True
        except (socket.error, FileNotFoundError, ConnectionRefusedError, OSError):
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    else:
        return True  # Always true in simulation mode

def preprocess_frame(frame, x, y, w, h):
    """Extract ROI and preprocess for model"""
    roi = frame[y:y+h, x:x+w]
    roi_resized = cv2.resize(roi, (IMG_SIZE, IMG_SIZE))
    roi_normalized = roi_resized.astype(np.float32) / 255.0
    roi_input = np.expand_dims(roi_normalized, axis=0)
    return roi_input

def predict_gesture(roi_input):
    """Run inference with TFLite model"""
    interpreter.set_tensor(input_details[0]['index'], roi_input)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    
    predicted_class = np.argmax(output_data[0])
    confidence = output_data[0][predicted_class] * 100
    
    return class_names[predicted_class], confidence

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ ERROR: Cannot open camera")
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Tracking variables
last_command_time = 0
last_volume_change_time = 0
gesture_start_time = None  # Time when current gesture started being detected
current_stable_gesture = None  # Currently stable gesture
last_detected_gesture = None
fps_start_time = time.time()
fps_frame_count = 0
fps = 0
latency_ms = 0  # End-to-end latency in milliseconds
is_playing = True  # Track video playback state (starts playing)

print("\n🎥 Camera ready! Show gestures in the green box.\n")
print("📺 Control Settings:")
print("   • Confidence: 90%+ required")
print("   • Hold time: 1.5 seconds to trigger action")
print("   • Forward/Reverse: ±10 seconds")
print("   • Volume: ±10% (1.5-second delay between changes)")
print("   • Play/Stop: State-based control\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Calculate FPS
    fps_frame_count += 1
    if fps_frame_count >= 10:
        fps_end_time = time.time()
        fps = fps_frame_count / (fps_end_time - fps_start_time)
        fps_start_time = fps_end_time
        fps_frame_count = 0
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Define ROI (center square)
    roi_size = 300
    x = (w - roi_size) // 2
    y = (h - roi_size) // 2
    
    # Draw ROI
    cv2.rectangle(frame, (x, y), (x + roi_size, y + roi_size), (0, 255, 0), 2)
    
    # Start latency measurement
    latency_start = time.time()
    
    # Preprocess and predict
    roi_input = preprocess_frame(frame, x, y, roi_size, roi_size)
    gesture, confidence = predict_gesture(roi_input)
    
    # End latency measurement
    latency_end = time.time()
    latency_ms = (latency_end - latency_start) * 1000  # Convert to milliseconds
    
    # 3-second hold time check
    if confidence >= CONFIDENCE_THRESHOLD:
        # If this is the same gesture as before, continue timing
        if current_stable_gesture == gesture:
            if gesture_start_time is not None:
                hold_duration = current_time - gesture_start_time
                if hold_duration >= GESTURE_HOLD_TIME:
                    stable_gesture = gesture
                else:
                    stable_gesture = None
            else:
                gesture_start_time = current_time
                stable_gesture = None
        else:
            # New gesture detected, reset timer
            current_stable_gesture = gesture
            gesture_start_time = current_time
            stable_gesture = None
    else:
        # Confidence too low, reset
        current_stable_gesture = None
        gesture_start_time = None
        stable_gesture = None
    
    # Execute command if stable gesture detected
    current_time = time.time()
    command_sent = False
    
    if stable_gesture:
        # State-based play/stop control
        if stable_gesture == 'play' and not is_playing:
            # Only play if currently paused
            if send_mpv_command('play'):
                is_playing = True
                command_sent = True
                last_detected_gesture = 'play'
        elif stable_gesture == 'stop' and is_playing:
            # Only pause if currently playing
            if send_mpv_command('stop'):
                is_playing = False
                command_sent = True
                last_detected_gesture = 'stop'
        # Volume gesture with shorter cooldown (continuous control)
        elif stable_gesture == 'volume_up':
            if current_time - last_volume_change_time >= VOLUME_CHANGE_INTERVAL:
                if send_mpv_command(stable_gesture):
                    last_volume_change_time = current_time
                    command_sent = True
        # Forward/Reverse with cooldown
        elif stable_gesture in ['forward', 'reverse']:
            if (current_time - last_command_time >= COMMAND_COOLDOWN and 
                stable_gesture != last_detected_gesture):
                if send_mpv_command(stable_gesture):
                    last_command_time = current_time
                    last_detected_gesture = stable_gesture
                    command_sent = True
    else:
        # Reset last detected gesture for forward/reverse when no stable gesture
        if current_time - last_command_time > COMMAND_COOLDOWN:
            if last_detected_gesture in ['forward', 'reverse']:
                last_detected_gesture = None
    
    # Check MPV status
    mpv_running = check_mpv_status()
    
    # Display video state
    if mpv_running:
        video_state = "PLAYING ▶" if is_playing else "PAUSED ⏸"
        state_color = (0, 255, 0) if is_playing else (255, 165, 0)  # Green for playing, Orange for paused
    else:
        video_state = "MPV Not Running ✗"
        state_color = (0, 0, 255)
    
    # Display info on frame
    info_y = 30
    cv2.putText(frame, f"Video: {video_state}", (10, info_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
    
    # Display FPS (top right)
    fps_text = f"FPS: {fps:.1f}"
    fps_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    fps_color = (0, 255, 0) if fps >= 15 else (0, 165, 255)  # Green if >=15, Orange if <15
    cv2.putText(frame, fps_text, (w - fps_size[0] - 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
    
    # Display Latency (below FPS)
    latency_text = f"Latency: {latency_ms:.1f}ms"
    latency_size = cv2.getTextSize(latency_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    latency_color = (0, 255, 0) if latency_ms < 200 else (0, 165, 255)  # Green if <200ms, Orange if >=200ms
    cv2.putText(frame, latency_text, (w - latency_size[0] - 10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, latency_color, 2)
    
    info_y += 35
    if stable_gesture:
        text = f"Gesture: {gesture} ({confidence:.1f}%) ✓ READY"
        color = (0, 255, 0)
    else:
        if confidence >= CONFIDENCE_THRESHOLD and gesture_start_time is not None:
            hold_duration = current_time - gesture_start_time
            remaining = GESTURE_HOLD_TIME - hold_duration
            text = f"Hold: {gesture} ({confidence:.1f}%) → {remaining:.1f}s to trigger"
            color = (255, 165, 0)  # Orange when holding
        elif confidence >= CONFIDENCE_THRESHOLD:
            text = f"Detecting: {gesture} ({confidence:.1f}%)"
            color = (255, 165, 0)
        else:
            text = f"Confidence too low: {gesture} ({confidence:.1f}%)"
            color = (0, 165, 255)
    
    cv2.putText(frame, text, (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if command_sent:
        info_y += 35
        action_text = "STARTED" if stable_gesture == 'play' else "PAUSED" if stable_gesture == 'stop' else stable_gesture.upper()
        cv2.putText(frame, f"-> {action_text}!", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Instructions
    cv2.putText(frame, "Press 'q' to quit | Hold gesture 1.5s at 90%+ confidence", (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('MPV Gesture Control', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✓ Gesture control stopped.")
