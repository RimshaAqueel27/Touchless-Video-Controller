import tensorflow as tf
import os

print("Converting model to TensorFlow Lite...")

# Load trained model
model = tf.keras.models.load_model("gesture_model.h5")

# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save TFLite model
with open("gesture_model.tflite", "wb") as f:
    f.write(tflite_model)

print("✓ Model converted to TensorFlow Lite successfully!")
print("File: gesture_model.tflite")

# Check model size
h5_size = os.path.getsize("gesture_model.h5") / (1024 * 1024)
tflite_size = os.path.getsize("gesture_model.tflite") / (1024 * 1024)

print(f"\nModel Sizes:")
print(f"  H5 Model:     {h5_size:.2f} MB")
print(f"  TFLite Model: {tflite_size:.2f} MB")
print(f"  Size Reduction: {((h5_size - tflite_size) / h5_size * 100):.1f}%")

# Save model info for Jetson compatibility
import json
gesture_classes = sorted([d for d in os.listdir("dataset") if os.path.isdir(os.path.join("dataset", d))])
model_info = {
    "class_names": gesture_classes,
    "input_shape": [128, 128, 3],
    "model_version": "v1.0"
}

with open("model_info.json", "w") as f:
    json.dump(model_info, f, indent=2)
print(f"\n✓ Model info saved: model_info.json")
