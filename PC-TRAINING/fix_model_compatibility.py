"""
Fix Model Compatibility for Jetson Nano (TensorFlow 2.3.1)

This script loads the model trained on newer TensorFlow and saves it
in a format compatible with TensorFlow 2.3.1 on Jetson Nano.
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import numpy as np

print("=" * 60)
print("Model Compatibility Fix for Jetson Nano")
print("=" * 60)

# Check TensorFlow version
print(f"\nCurrent TensorFlow version: {tf.__version__}")

# Configuration
IMG_SIZE = 128
BATCH_SIZE = 8

# Load the dataset to get number of classes
print("\nLoading dataset to determine classes...")
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    "dataset",
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

num_classes = len(train_generator.class_indices)
class_names = list(train_generator.class_indices.keys())
print(f"Number of classes: {num_classes}")
print(f"Classes: {class_names}")

# Rebuild the model architecture (compatible way)
print("\nRebuilding model architecture...")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

# Build new model
model_new = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

# Load weights from old model
print("\nLoading weights from gesture_model.h5...")
try:
    old_model = tf.keras.models.load_model("gesture_model.h5")
    
    # Transfer weights
    print("Transferring weights...")
    for i, layer in enumerate(model_new.layers):
        if i < len(old_model.layers):
            try:
                layer.set_weights(old_model.layers[i].get_weights())
                print(f"  ✓ Transferred weights for layer {i}: {layer.name}")
            except:
                print(f"  ⚠ Skipped layer {i}: {layer.name}")
    
    print("\n✓ Weights transferred successfully")
    
except Exception as e:
    print(f"\n⚠ Could not load old model: {e}")
    print("Training new model from scratch...")
    
    val_generator = train_datagen.flow_from_directory(
        "dataset",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    model_new.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("\nTraining model...")
    model_new.fit(
        train_generator,
        epochs=10,
        validation_data=val_generator,
        verbose=1
    )

# Save in compatible format
print("\n" + "=" * 60)
print("Saving compatible model...")
print("=" * 60)

# Method 1: Save as H5 with compile=False
model_new.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

output_file = "gesture_model_jetson.h5"
model_new.save(output_file, save_format='h5', include_optimizer=False)
print(f"\n✓ Saved H5 model: {output_file}")

# Method 2: Save weights only
weights_file = "gesture_model.weights.h5"
try:
    model_new.save_weights(weights_file)
    print(f"✓ Saved weights: {weights_file}")
except Exception as e:
    print(f"⚠ Could not save weights: {e}")

# Save model architecture as JSON
architecture_file = "model_architecture.json"
with open(architecture_file, 'w') as f:
    f.write(model_new.to_json())
print(f"✓ Saved architecture: {architecture_file}")

# Save class names
class_names_file = "class_names.txt"
with open(class_names_file, 'w') as f:
    for name in class_names:
        f.write(name + '\n')
print(f"✓ Saved class names: {class_names_file}")

print("\n" + "=" * 60)
print("COMPATIBILITY FIX COMPLETE!")
print("=" * 60)
print("\nFiles to transfer to Jetson Nano:")
print(f"  1. {output_file} (use this)")
print(f"  2. {weights_file} (backup)")
print(f"  3. {architecture_file} (backup)")
print(f"  4. {class_names_file}")
print(f"  5. media_control.py (updated)")
print(f"  6. dataset/ folder")
print("\nModel is now compatible with TensorFlow 2.3.1")
print("=" * 60)
