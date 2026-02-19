import tensorflow as tf
import numpy as np
import json
import os

print("="*60)
print("Creating TensorFlow Lite model for Jetson Nano")
print("="*60)

# Load the trained model
print("\nLoading gesture_model.h5...")
model = tf.keras.models.load_model("gesture_model.h5")
print("✓ Model loaded successfully")

# Get class names from dataset
gesture_classes = sorted([d for d in os.listdir("dataset") if os.path.isdir(os.path.join("dataset", d))])
print(f"✓ Found {len(gesture_classes)} classes: {gesture_classes}")

# Convert to TensorFlow Lite with compatibility for TF 2.3.1
print("\nConverting to TensorFlow Lite (compatible mode)...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable compatibility with older TensorFlow versions
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,  # Enable TensorFlow Lite ops
    tf.lite.OpsSet.SELECT_TF_OPS      # Enable TensorFlow ops (fallback)
]
converter._experimental_lower_tensor_list_ops = False

print("  Targeting TensorFlow 2.3.1 compatibility...")
tflite_model = converter.convert()

# Save TFLite model
tflite_filename = "gesture_model.tflite"
with open(tflite_filename, "wb") as f:
    f.write(tflite_model)
print(f"✓ TFLite model created: {tflite_filename}")

# Get model size comparison
h5_size = os.path.getsize("gesture_model.h5") / (1024 * 1024)
tflite_size = os.path.getsize(tflite_filename) / (1024 * 1024)
print(f"\nModel Sizes:")
print(f"  H5 Model:     {h5_size:.2f} MB")
print(f"  TFLite Model: {tflite_size:.2f} MB")
print(f"  Size Reduction: {((h5_size - tflite_size) / h5_size * 100):.1f}%")

# Test the TFLite model
print("\nTesting TFLite model...")
interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"  Input shape: {input_details[0]['shape']}")
print(f"  Input dtype: {input_details[0]['dtype']}")
print(f"  Output shape: {output_details[0]['shape']}")

# Run test inference
test_input = np.random.rand(1, 128, 128, 3).astype(np.float32)
interpreter.set_tensor(input_details[0]['index'], test_input)
interpreter.invoke()
test_output = interpreter.get_tensor(output_details[0]['index'])
print(f"✓ Test inference successful - Output shape: {test_output.shape}")

# Save model info (Jetson-compatible format)
model_info = {
    "class_names": gesture_classes,
    "input_shape": [128, 128, 3],
    "model_version": "v1.0"
}

info_filename = "model_info.json"
with open(info_filename, "w") as f:
    json.dump(model_info, f, indent=2)
print(f"✓ Model info saved: {info_filename}")

print("\n" + "="*60)
print("TFLITE CONVERSION COMPLETE!")
print("="*60)
print("\nFiles created:")
print(f"  1. {tflite_filename} ({tflite_size:.2f} MB)")
print(f"  2. {info_filename}")
print("\nTransfer these files to Jetson Nano along with:")
print("  3. media_control_mpv.py")
print("\nThen run: python3 media_control_mpv.py")
print("="*60)
