import numpy as np
from data_preparation.data_preparation import generate_synthetic_data, load_data
from model import create_model
from tensorflow.keras.utils import to_categorical

# Generate synthetic data
num_synthetic_samples = 1000
synthetic_data, synthetic_labels = generate_synthetic_data(num_synthetic_samples)

# Load real data
data_dir = 'synthetic_data'  # Path to real data directory
real_data, real_labels = load_data(data_dir)

# Ensure the data is of correct shape
print(f"Synthetic data shape: {synthetic_data.shape}")
print(f"Real data shape: {real_data.shape}")
print(f"Synthetic labels shape: {synthetic_labels.shape}")
print(f"Real labels shape: {real_labels.shape}")

# Normalize data
synthetic_data = synthetic_data / 255.0
real_data = real_data / 255.0

# Combine synthetic and real data
data = np.concatenate((synthetic_data, real_data), axis=0)
labels = np.concatenate((synthetic_labels, real_labels), axis=0)

# Ensure labels are one-hot encoded
num_classes = 7  # Adjust this if your number of classes is different
labels = to_categorical(labels, num_classes=num_classes)

# Print shapes after preprocessing
print(f"Combined data shape: {data.shape}")
print(f"Combined labels shape: {labels.shape}")

# Create and compile the model
model = create_model(input_shape=data.shape[1:], num_classes=num_classes)

# Compile the model with categorical_crossentropy loss
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(data, labels, epochs=10, batch_size=32, validation_split=0.2)

# Save the model
model.save('model.h5')

# Optional: Plot training & validation accuracy and loss
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

# Plot training & validation accuracy
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(['Train', 'Validation'], loc='upper left')

# Plot training & validation loss
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Train', 'Validation'], loc='upper left')

plt.show()
