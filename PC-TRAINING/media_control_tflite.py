import cv2
import numpy as np
import tensorflow as tf
import json
import time
import subprocess
import platform
import os

print("="*60)
print("GESTURE-BASED MEDIA CONTROL SYSTEM (TFLite)")
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
COOLDOWN_TIME = 2.0  # Seconds between gesture commands
last_action_time = 0
last_gesture = None

# ==================== MEDIA CONTROL FUNCTIONS ====================
def execute_media_command(gesture):
    """Execute media player commands based on recognized gesture."""
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
                subprocess.run(commands[gesture], check=False, 
                             stderr=subprocess.DEVNULL, 
                             stdout=subprocess.DEVNULL,
                             timeout=1)
                print(f"✓ Executed: {gesture}")
            else:
                print(f"[SIMULATION] Would execute: {gesture}")
        except subprocess.TimeoutExpired:
            print(f"⚠ Command timeout: {gesture}")
        except Exception as e:
            print(f"⚠ Command error: {e}")

# ==================== CAMERA SETUP ====================
print("\nInitializing camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera 0 not available, trying camera 1...")
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ ERROR: Could not open camera!")
    print("Available cameras:")
    for i in range(5):
        test_cap = cv2.VideoCapture(i)
        if test_cap.isOpened():
            print(f"  - Camera {i} available")
            test_cap.release()
    exit(1)

print("✓ Camera opened successfully")

# Set camera properties for better performance on Jetson
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\n" + "="*60)
print("SYSTEM CONFIGURATION")
print("="*60)
print(f"Platform: {platform.machine()}")
print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}%")
print(f"Cooldown Time: {COOLDOWN_TIME}s")
print(f"Image Size: {IMG_SIZE}x{IMG_SIZE}")
print("\nGesture Mappings:")
action_map = {
    'play': 'Play/Pause',
    'stop': 'Stop',
    'forward': 'Next Track',
    'reverse': 'Previous Track',
    'volume_up': 'Volume +10%',
    'volume_down': 'Volume -10%'
}
for gesture in gesture_classes:
    print(f"  {gesture:12} → {action_map.get(gesture, 'Unknown')}")
print("\nPress 'q' to quit")
print("="*60 + "\n")

# ==================== MAIN LOOP ====================
frame_count = 0
fps_start_time = time.time()
fps = 0

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

        # Apply confidence threshold and cooldown logic
        action_status = "WAITING..."
        status_color = (200, 200, 200)
        
        if confidence >= CONFIDENCE_THRESHOLD:
            time_since_last = current_time - last_action_time
            
            if time_since_last >= COOLDOWN_TIME:
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

        # Display info on frame
        cv2.putText(frame, f"Gesture: {predicted_gesture}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, action_status, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Show all probabilities
        y_pos = 160
        for i, gesture in enumerate(gesture_classes):
            prob = predictions[i] * 100
            color = (0, 255, 0) if i == predicted_class_idx else (255, 255, 255)
            cv2.putText(frame, f"{gesture}: {prob:.1f}%", (10, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_pos += 25

        cv2.imshow("Gesture Media Control [TFLite]", frame)
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
