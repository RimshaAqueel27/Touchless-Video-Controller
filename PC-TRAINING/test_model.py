import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os

# Limit GPU memory growth to prevent OOM errors on Jetson Nano
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"GPU configuration error: {e}")

# Load the trained model (with compatibility fallback)
model = None

# Try loading compatible version first
if os.path.exists("gesture_model_jetson.h5"):
    try:
        model = load_model("gesture_model_jetson.h5", compile=False)
        print("✓ Loaded gesture_model_jetson.h5")
    except Exception as e:
        print(f"⚠ Could not load gesture_model_jetson.h5: {e}")

# Fallback to original
if model is None and os.path.exists("gesture_model.h5"):
    try:
        model = load_model("gesture_model.h5", compile=False)
        print("✓ Loaded gesture_model.h5")
    except Exception as e:
        print(f"⚠ Could not load gesture_model.h5: {e}")

# Fallback to architecture + weights
weights_files = ["gesture_model.weights.h5", "gesture_model_weights.h5"]
if model is None and os.path.exists("model_architecture.json"):
    for weights_file in weights_files:
        if os.path.exists(weights_file):
            try:
                with open("model_architecture.json", 'r') as f:
                    model = tf.keras.models.model_from_json(f.read())
                model.load_weights(weights_file)
                print("✓ Loaded from architecture + weights")
                break
            except Exception as e:
                print(f"⚠ Could not load from {weights_file}: {e}")

if model is None:
    print("ERROR: Could not load model! Run fix_model_compatibility.py first.")
    exit(1)

# Get gesture class names
if os.path.exists("class_names.txt"):
    gesture_classes = []
    with open("class_names.txt", 'r') as f:
        gesture_classes = [line.strip() for line in f.readlines()]
else:
    gesture_classes = sorted(os.listdir("dataset"))

print(f"Loaded model with classes: {gesture_classes}")

IMG_SIZE = 128

# Try external webcam (usually index 1)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("External webcam not found. Trying default camera...")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open any camera!")
    exit(1)

print("Camera opened successfully. Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for mirror effect
    frame = cv2.flip(frame, 1)

    # Draw ROI (Region of Interest)
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

    # Display prediction on frame
    cv2.putText(frame, f"Gesture: {predicted_gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Confidence: {confidence:.2f}%", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display all class probabilities
    y_pos = 120
    for i, gesture in enumerate(gesture_classes):
        prob = predictions[0][i] * 100
        color = (0, 255, 0) if i == predicted_class_idx else (255, 255, 255)
        cv2.putText(frame, f"{gesture}: {prob:.2f}%", (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y_pos += 25

    cv2.imshow("Gesture Recognition", frame)
    cv2.imshow("ROI", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
