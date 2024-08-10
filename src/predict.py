import numpy as np
from model import load_trained_model
from data_preparation import load_data  # Import the load_data function

# Load the model
model = load_trained_model('model.h5')

# Load new data for prediction
data_dir = 'synthetic_data'  # Path to the data directory
new_data, _ = load_data(data_dir)

# Debugging: Check if data is loaded
if new_data.size == 0:
    raise ValueError("Data is empty. Please check the data directory and files.")
else:
    print(f"Data loaded successfully with shape: {new_data.shape}")

# Normalize data
new_data = new_data / 255.0

# Make predictions
predictions = model.predict(new_data)

# Convert predictions from one-hot encoding to class labels
predicted_classes = np.argmax(predictions, axis=1)

print(f'Predictions: {predicted_classes}')
