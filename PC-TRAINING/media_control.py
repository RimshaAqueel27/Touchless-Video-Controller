import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import time
import subprocess
import platform

# Limit GPU memory growth on Jetson Nano
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"GPU configuration error: {e}")

# ==================== CONFIGURATION ====================
IMG_SIZE = 128
CONFIDENCE_THRESHOLD = 75.0  # Minimum confidence to trigger action
COOLDOWN_TIME = 2.0  # Seconds between gesture commands
last_action_time = 0
last_gesture = None

# Load model (with fallback for compatibility)
model = None
gesture_classes = None

# Try loading from compatible H5 first
if os.path.exists("gesture_model_jetson.h5"):
    try:
        print("Loading gesture_model_jetson.h5...")
        model = load_model("gesture_model_jetson.h5", compile=False)
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"⚠ Could not load gesture_model_jetson.h5: {e}")

# Fallback to original model
if model is None and os.path.exists("gesture_model.h5"):
    try:
        print("Loading gesture_model.h5...")
        model = load_model("gesture_model.h5", compile=False)
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"⚠ Could not load gesture_model.h5: {e}")

# Fallback to loading from architecture + weights
weights_files = ["gesture_model.weights.h5", "gesture_model_weights.h5"]
if model is None and os.path.exists("model_architecture.json"):
    for weights_file in weights_files:
        if os.path.exists(weights_file):
            try:
                print(f"Loading from architecture + {weights_file}...")
                with open("model_architecture.json", 'r') as f:
                    model = tf.keras.models.model_from_json(f.read())
                model.load_weights(weights_file)
                print("✓ Model loaded from architecture + weights")
                break
            except Exception as e:
                print(f"⚠ Could not load from {weights_file}: {e}")

if model is None:
    print("ERROR: Could not load model!")
    print("Please run fix_model_compatibility.py on PC and transfer gesture_model_jetson.h5")
    exit(1)

# Load class names
if os.path.exists("class_names.txt"):
    gesture_classes = []
    with open("class_names.txt", 'r') as f:
        gesture_classes = [line.strip() for line in f.readlines()]
    print(f"Loaded classes from file: {gesture_classes}")
else:
    gesture_classes = sorted(os.listdir("dataset"))
    print(f"Loaded classes from dataset folder: {gesture_classes}")

# ==================== MEDIA CONTROL FUNCTIONS ====================
def execute_media_command(gesture):
    """
    Execute media player commands based on recognized gesture.
    Uses VLC media player commands (works on Linux/Jetson Nano).
    """
    is_jetson = platform.machine() == 'aarch64'
    
    commands = {
        'play': ['dbus-send', '--type=method_call', '--dest=org.mpris.MediaPlayer2.vlc',
                 '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.PlayPause'],
        'stop': ['dbus-send', '--type=method_call', '--dest=org.mpris.MediaPlayer2.vlc',
                 '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.Stop'],
        'forward': ['dbus-send', '--type=method_call', '--dest=org.mpris.MediaPlayer2.vlc',
                    '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.Next'],
        'reverse': ['dbus-send', '--type=method_call', '--dest=org.mpris.MediaPlayer2.vlc',
                    '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.Previous'],
        'volume_up': ['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'],
        'volume_down': ['amixer', '-D', 'pulse', 'sset', 'Master', '10%-']
    }
    
    if gesture in commands:
        try:
            if is_jetson:
                subprocess.run(commands[gesture], check=False, stderr=subprocess.DEVNULL)
                print(f"✓ Executed: {gesture}")
            else:
                print(f"[SIMULATION] Would execute: {gesture}")
        except Exception as e:
            print(f"Command error: {e}")

# ==================== CAMERA SETUP ====================
cap = cv2.VideoCapture(1 if platform.machine() == 'aarch64' else 0)

if not cap.isOpened():
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera!")
    exit(1)

print("=" * 50)
print("GESTURE-BASED MEDIA CONTROL SYSTEM")
print("=" * 50)
print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}%")
print(f"Cooldown Time: {COOLDOWN_TIME}s")
print("\nGesture Mappings:")
print("  play       → Play/Pause")
print("  stop       → Stop")
print("  forward    → Next Track")
print("  reverse    → Previous Track")
print("  volume_up  → Increase Volume")
print("  volume_down→ Decrease Volume")
print("\nPress 'q' to quit")
print("=" * 50)

# ==================== MAIN LOOP ====================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    current_time = time.time()

    # Draw ROI
    cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 2)

    # Extract and preprocess ROI
    roi = frame[100:400, 100:400]
    roi_resized = cv2.resize(roi, (IMG_SIZE, IMG_SIZE))
    roi_normalized = roi_resized / 255.0
    roi_input = np.expand_dims(roi_normalized, axis=0)

    # Predict
    predictions = model.predict(roi_input, verbose=0)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class_idx] * 100
    predicted_gesture = gesture_classes[predicted_class_idx]

    # Apply confidence threshold and cooldown logic
    action_status = "WAITING..."
    status_color = (200, 200, 200)
    
    if confidence >= CONFIDENCE_THRESHOLD:
        time_since_last = current_time - last_action_time
        
        if time_since_last >= COOLDOWN_TIME:
            # Execute command
            execute_media_command(predicted_gesture)
            last_action_time = current_time
            last_gesture = predicted_gesture
            action_status = f"EXECUTED: {predicted_gesture.upper()}"
            status_color = (0, 255, 0)
        else:
            remaining = COOLDOWN_TIME - time_since_last
            action_status = f"COOLDOWN: {remaining:.1f}s"
            status_color = (0, 165, 255)
    else:
        action_status = f"LOW CONFIDENCE ({confidence:.1f}%)"
        status_color = (0, 0, 255)

    # Display info
    cv2.putText(frame, f"Gesture: {predicted_gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, action_status, (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

    # Show all probabilities
    y_pos = 160
    for i, gesture in enumerate(gesture_classes):
        prob = predictions[0][i] * 100
        color = (0, 255, 0) if i == predicted_class_idx else (255, 255, 255)
        cv2.putText(frame, f"{gesture}: {prob:.1f}%", (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y_pos += 25

    cv2.imshow("Gesture Media Control", frame)
    cv2.imshow("ROI", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
