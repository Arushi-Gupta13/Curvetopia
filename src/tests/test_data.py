import sys
import os
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to system path (two levels up to include 'src')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import necessary modules from the src package
from src.model import load_trained_model
from src.data_preparation.data_preparation import load_data

try:
    # Load the model
    model = load_trained_model(os.path.join(os.path.dirname(__file__), '..', '..', 'model.h5'))

    # Load and preprocess test data
    test_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data/problems')
    test_data, test_labels = load_data(test_data_dir, add_shape_in_folder=False)

    # Normalize test data
    test_data = test_data / 255.0

    # Make predictions
    predictions = model.predict(test_data)
    predicted_classes = np.argmax(predictions, axis=1)

    # Evaluate performance
    accuracy = accuracy_score(test_labels, predicted_classes)
    print(f'Accuracy: {accuracy:.2f}')

    # Detailed classification report
    class_names = ['ellipse', 'circle', 'rounded_rectangle', 'rectangle', 'square', 'triangle', 'star']
    report = classification_report(test_labels, predicted_classes, target_names=class_names)
    print(report)

    # Confusion matrix
    conf_matrix = confusion_matrix(test_labels, predicted_classes)
    plt.figure(figsize=(10, 7))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.show()

except Exception as e:
    print(f"An error occurred: {e}")
