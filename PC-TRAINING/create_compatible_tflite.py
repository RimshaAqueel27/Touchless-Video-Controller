import tensorflow as tf
import numpy as np
import json
import os

print("="*60)
print("Creating TFLite Model - Maximum Compatibility Mode")
print("="*60)

# Load the trained model
print("\nLoading gesture_model.h5...")
model = tf.keras.models.load_model("gesture_model.h5")
print("✓ Model loaded successfully")

# Get class names from dataset
gesture_classes = sorted([d for d in os.listdir("dataset") if os.path.isdir(os.path.join("dataset", d))])
print(f"✓ Found {len(gesture_classes)} classes: {gesture_classes}")

# Try multiple conversion strategies
print("\n" + "="*60)
print("Trying Multiple Conversion Strategies")
print("="*60)

# Strategy 1: No optimization (most compatible)
print("\n[1/2] Strategy 1: No optimization (maximum compatibility)...")
try:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # No optimizations - use basic operations only
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    tflite_model_v1 = converter.convert()
    
    with open("gesture_model_v1.tflite", "wb") as f:
        f.write(tflite_model_v1)
    
    v1_size = os.path.getsize("gesture_model_v1.tflite") / (1024 * 1024)
    print(f"  ✓ Created: gesture_model_v1.tflite ({v1_size:.2f} MB)")
    print("  ✓ This version should work on TF 2.3.1!")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Strategy 2: With TF ops fallback
print("\n[2/2] Strategy 2: With TensorFlow ops fallback...")
try:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    tflite_model_v2 = converter.convert()
    
    with open("gesture_model_v2.tflite", "wb") as f:
        f.write(tflite_model_v2)
    
    v2_size = os.path.getsize("gesture_model_v2.tflite") / (1024 * 1024)
    print(f"  ✓ Created: gesture_model_v2.tflite ({v2_size:.2f} MB)")
    print("  ✓ Optimized but with TF ops")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test both models
print("\n" + "="*60)
print("Testing Models")
print("="*60)

for version in ["v1", "v2"]:
    filename = f"gesture_model_{version}.tflite"
    if os.path.exists(filename):
        try:
            print(f"\nTesting {filename}...")
            interpreter = tf.lite.Interpreter(model_path=filename)
            interpreter.allocate_tensors()
            
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            # Run test inference
            test_input = np.random.rand(1, 128, 128, 3).astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], test_input)
            interpreter.invoke()
            test_output = interpreter.get_tensor(output_details[0]['index'])
            
            print(f"  ✓ Test passed - Output shape: {test_output.shape}")
            print(f"  ✓ Ready for Jetson Nano!")
        except Exception as e:
            print(f"  ✗ Test failed: {e}")

# Save model info
model_info = {
    "class_names": gesture_classes,
    "input_shape": [128, 128, 3],
    "model_version": "v1.0"
}

with open("model_info.json", "w") as f:
    json.dump(model_info, f, indent=2)
print("\n✓ Model info saved: model_info.json")

# Size comparison
h5_size = os.path.getsize("gesture_model.h5") / (1024 * 1024)
print("\n" + "="*60)
print("SIZE COMPARISON")
print("="*60)
print(f"Original H5 model: {h5_size:.2f} MB")

if os.path.exists("gesture_model_v1.tflite"):
    v1_size = os.path.getsize("gesture_model_v1.tflite") / (1024 * 1024)
    print(f"TFLite v1 (no opt): {v1_size:.2f} MB ({((h5_size-v1_size)/h5_size*100):.1f}% reduction)")

if os.path.exists("gesture_model_v2.tflite"):
    v2_size = os.path.getsize("gesture_model_v2.tflite") / (1024 * 1024)
    print(f"TFLite v2 (optimized): {v2_size:.2f} MB ({((h5_size-v2_size)/h5_size*100):.1f}% reduction)")

print("\n" + "="*60)
print("TRANSFER INSTRUCTIONS")
print("="*60)
print("\n📦 RECOMMENDED: Transfer these files to Jetson Nano:")
print("  1. gesture_model_v1.tflite  (RECOMMENDED - most compatible)")
print("  2. model_info.json")
print("  3. media_control_mpv.py")
print("\n📦 ALTERNATIVE: If v1 doesn't work, try:")
print("  1. gesture_model_v2.tflite  (needs SELECT_TF_OPS support)")
print("  2. model_info.json")
print("  3. media_control_mpv.py")
print("\n🚀 On Jetson Nano:")
print("  # Rename v1 to standard name:")
print("  cp gesture_model_v1.tflite gesture_model.tflite")
print("  python3 media_control_mpv.py")
print("="*60)
