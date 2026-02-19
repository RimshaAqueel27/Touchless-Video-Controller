import cv2
import numpy as np
import tensorflow as tf
import json
import time
import subprocess
import platform
import os

print("="*60)
print("GESTURE-BASED MEDIA CONTROL SYSTEM (TFLite + MPV)")
print("="*60)

# ==================== LOAD MODEL ====================
try:
    # Load TFLite model
    print("\nLoading gesture_model.tflite...")
    interpreter = tf.lite.Interpreter(model_path="gesture_model.tflite")
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("✓ TFLite model loaded successfully")
    
    # Load model info
    print("Loading model_info.json...")
    with open("model_info.json", "r") as f:
        model_info = json.load(f)
    gesture_classes = model_info["classes"]
    IMG_SIZE = model_info.get("img_size", 128)
    print(f"✓ Loaded {len(gesture_classes)} gesture classes")
    print(f"  Classes: {gesture_classes}")
    
except Exception as e:
    print(f"\n❌ ERROR: Could not load model - {e}")
    print("\nMake sure you have transferred:")
    print("  1. gesture_model.tflite")
    print("  2. model_info.json")
    print("\nRun create_tflite_model.py on PC first!")
    exit(1)

# ==================== CONFIGURATION ====================
CONFIDENCE_THRESHOLD = 75.0  # Minimum confidence to trigger action
COOLDOWN_TIME = 1.5  # Seconds between non-volume commands
VOLUME_CHANGE_INTERVAL = 0.3  # Seconds between volume changes (continuous)
last_action_time = 0
last_volume_change_time = 0
last_gesture = None
gesture_hold_start = 0
is_jetson = platform.machine() == 'aarch64'

# ==================== MEDIA CONTROL FUNCTIONS ====================
def execute_media_command(gesture):
    """Execute MPV media player commands using playerctl."""
    global last_action_time
    
    # MPV commands using playerctl (MPRIS2 interface)
    commands = {
        'play': ['playerctl', '-p', 'mpv', 'play-pause'],
        'stop': ['playerctl', '-p', 'mpv', 'stop'],
        'forward': ['playerctl', '-p', 'mpv', 'position', '10+'],  # Skip forward 10s
        'reverse': ['playerctl', '-p', 'mpv', 'position', '10-'],  # Skip backward 10s
    }
    
    if gesture in commands:
        try:
            if is_jetson:
                result = subprocess.run(commands[gesture], check=False, 
                             stderr=subprocess.DEVNULL, 
                             stdout=subprocess.DEVNULL,
                             timeout=1)
                if result.returncode == 0:
                    print(f"✓ MPV: {gesture}")
                    last_action_time = time.time()
                    return True
                else:
                    print(f"⚠ MPV not responding (is it running?)")
                    return False
            else:
                print(f"[SIMULATION] MPV {gesture}")
                last_action_time = time.time()
                return True
        except FileNotFoundError:
            print(f"⚠ playerctl not found. Install: sudo apt-get install playerctl")
            return False
        except Exception as e:
            print(f"⚠ Error: {e}")
            return False
    return False

def change_volume(direction):
    """
    Change system volume continuously while gesture is held.
    Direction: 'up' or 'down'
    Changes by 5% increments.
    """
    global last_volume_change_time
    
    try:
        if direction == 'up':
            command = ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%']
        else:
            command = ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%']
        
        if is_jetson:
            result = subprocess.run(command, check=False, 
                         stderr=subprocess.DEVNULL, 
                         stdout=subprocess.DEVNULL,
                         timeout=0.5)
            if result.returncode == 0:
                last_volume_change_time = time.time()
                return True
        else:
            print(f"[SIMULATION] Volume {direction} 5%")
            last_volume_change_time = time.time()
            return True
    except:
        pass
    return False

# ==================== CAMERA SETUP ====================
print("\nInitializing camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera 0 not available, trying camera 1...")
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ ERROR: Could not open camera!")
    exit(1)

print("✓ Camera opened successfully")

# Set camera properties for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\n" + "="*60)
print("SYSTEM CONFIGURATION")
print("="*60)
print(f"Platform: {platform.machine()}")
print(f"Media Player: MPV (via playerctl)")
print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}%")
print(f"Cooldown Time: {COOLDOWN_TIME}s")
print(f"Volume Change Interval: {VOLUME_CHANGE_INTERVAL}s")
print(f"Image Size: {IMG_SIZE}x{IMG_SIZE}")
print("\nGesture Mappings:")
action_map = {
    'play': 'Play/Pause',
    'stop': 'Stop Playback',
    'forward': 'Skip Forward 10s',
    'reverse': 'Skip Backward 10s',
    'volume_up': 'Volume +5% (hold for continuous)',
    'volume_down': 'Volume -5% (hold for continuous)'
}
for gesture in gesture_classes:
    print(f"  {gesture:12} → {action_map.get(gesture, 'Unknown')}")
print("\nImportant: MPV must be running!")
print("  Start MPV with: mpv --idle --force-window video.mp4")
print("\nPress 'q' to quit")
print("="*60 + "\n")

# Check if playerctl is available
if is_jetson:
    try:
        result = subprocess.run(['which', 'playerctl'], capture_output=True)
        if result.returncode != 0:
            print("⚠ WARNING: playerctl not found!")
            print("  Install: sudo apt-get install playerctl")
            print()
    except:
        pass

# ==================== MAIN LOOP ====================
frame_count = 0
fps_start_time = time.time()
fps = 0
previous_gesture = None
gesture_stable_count = 0
STABLE_FRAMES_REQUIRED = 3  # Frames to confirm gesture

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ Failed to read frame")
            break

        frame = cv2.flip(frame, 1)
        current_time = time.time()
        
        # Calculate FPS
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = current_time - fps_start_time
            if elapsed > 0:
                fps = 30 / elapsed
            fps_start_time = current_time

        # Draw ROI
        cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 2)

        # Extract and preprocess ROI
        roi = frame[100:400, 100:400]
        roi_resized = cv2.resize(roi, (IMG_SIZE, IMG_SIZE))
        roi_normalized = roi_resized.astype(np.float32) / 255.0
        roi_input = np.expand_dims(roi_normalized, axis=0)

        # Run inference with TFLite
        interpreter.set_tensor(input_details[0]['index'], roi_input)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        
        predicted_class_idx = np.argmax(predictions)
        confidence = predictions[predicted_class_idx] * 100
        predicted_gesture = gesture_classes[predicted_class_idx]

        # Gesture stability check (reduce false triggers)
        if predicted_gesture == previous_gesture:
            gesture_stable_count += 1
        else:
            gesture_stable_count = 0
            previous_gesture = predicted_gesture

        # Apply confidence threshold and execute commands
        action_status = "WAITING..."
        status_color = (200, 200, 200)
        
        if confidence >= CONFIDENCE_THRESHOLD and gesture_stable_count >= STABLE_FRAMES_REQUIRED:
            
            # Handle VOLUME gestures (continuous while holding)
            if predicted_gesture in ['volume_up', 'volume_down']:
                time_since_last_volume = current_time - last_volume_change_time
                
                if time_since_last_volume >= VOLUME_CHANGE_INTERVAL:
                    direction = 'up' if predicted_gesture == 'volume_up' else 'down'
                    if change_volume(direction):
                        action_status = f"VOLUME {direction.upper()} (+5%)"
                        status_color = (0, 255, 255)  # Cyan
                        last_gesture = predicted_gesture
                    else:
                        action_status = "VOLUME CHANGE FAILED"
                        status_color = (0, 0, 255)
                else:
                    action_status = f"CHANGING... (hold gesture)"
                    status_color = (0, 255, 255)
            
            # Handle OTHER gestures (with cooldown)
            elif predicted_gesture in ['play', 'stop', 'forward', 'reverse']:
                time_since_last = current_time - last_action_time
                
                if time_since_last >= COOLDOWN_TIME:
                    if execute_media_command(predicted_gesture):
                        last_gesture = predicted_gesture
                        action_status = f"EXECUTED: {predicted_gesture.upper()}"
                        status_color = (0, 255, 0)
                    else:
                        action_status = "COMMAND FAILED"
                        status_color = (0, 0, 255)
                else:
                    remaining = COOLDOWN_TIME - time_since_last
                    action_status = f"COOLDOWN: {remaining:.1f}s"
                    status_color = (0, 165, 255)
        else:
            if confidence < CONFIDENCE_THRESHOLD:
                action_status = f"LOW CONFIDENCE ({confidence:.1f}%)"
                status_color = (0, 0, 255)
            else:
                action_status = "STABILIZING..."
                status_color = (100, 100, 100)

        # Display info on frame
        cv2.putText(frame, f"Gesture: {predicted_gesture}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, action_status, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # MPV status indicator
        mpv_status = "MPV: Running" if is_jetson else "MPV: Simulation"
        cv2.putText(frame, mpv_status, (450, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show all probabilities
        y_pos = 160
        for i, gesture in enumerate(gesture_classes):
            prob = predictions[i] * 100
            color = (0, 255, 0) if i == predicted_class_idx else (255, 255, 255)
            cv2.putText(frame, f"{gesture}: {prob:.1f}%", (10, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_pos += 25

        cv2.imshow("MPV Gesture Control [TFLite]", frame)
        cv2.imshow("ROI", roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nQuitting...")
            break

except KeyboardInterrupt:
    print("\n\nInterrupted by user")
except Exception as e:
    print(f"\n\n❌ ERROR: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Camera released")
    print("✓ Program terminated")
