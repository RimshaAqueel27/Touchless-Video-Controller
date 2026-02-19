import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Limit GPU memory growth to prevent OOM errors on Jetson Nano
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"GPU memory growth enabled for {len(gpus)} GPU(s)")
    except RuntimeError as e:
        print(f"GPU configuration error: {e}")

IMG_SIZE = 128
BATCH_SIZE = 8  # Reduced from 16 for Jetson Nano's limited memory

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    "dataset",
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    "dataset",
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Auto-detect number of classes from dataset
num_classes = len(train_generator.class_indices)
print(f"Number of classes detected: {num_classes}")
print(f"Classes: {list(train_generator.class_indices.keys())}")

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(num_classes, activation='softmax')  # Auto-detected from dataset
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nStarting training...")
history = model.fit(
    train_generator, 
    epochs=10, 
    validation_data=val_generator,
    verbose=1
)

print("\nSaving model...")
model.save("gesture_model.h5")
print("Model saved successfully as 'gesture_model.h5'!")
