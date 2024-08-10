import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

def generate_synthetic_data(num_samples, img_size=64, save_dir='synthetic_data'):
    # Create directories for each shape class
    shape_classes = ['ellipse', 'circle', 'rounded_rectangle', 'rectangle', 'square', 'triangle', 'star']
    os.makedirs(save_dir, exist_ok=True)
    for shape in shape_classes:
        os.makedirs(os.path.join(save_dir, shape), exist_ok=True)

    data = []
    labels = []

    for i in range(num_samples):
        img = np.zeros((img_size, img_size), dtype=np.uint8)

        # Generate a random shape
        shape = np.random.choice(shape_classes)

        # Initialize label to a default value
        label = -1

        if shape == 'ellipse':
            # Generate ellipse
            center = (np.random.randint(10, 50), np.random.randint(10, 50))
            axes = (np.random.randint(5, 25), np.random.randint(5, 25))
            angle = np.random.randint(0, 360)
            cv2.ellipse(img, center, axes, angle, 0, 360, 255, -1)  # Use white (255)
            label = 0
        
        elif shape == 'circle':
            # Generate circle
            center = (np.random.randint(10, 50), np.random.randint(10, 50))
            radius = np.random.randint(5, 25)
            cv2.circle(img, center, radius, 255, -1)  # Use white (255)
            label = 1
        
        elif shape == 'rounded_rectangle':
            # Generate rounded rectangle
            pt1 = (np.random.randint(5, 40), np.random.randint(5, 40))
            pt2 = (np.random.randint(5, 55), np.random.randint(5, 55))
            radius = np.random.randint(3, 10)
            cv2.rectangle(img, pt1, pt2, 255, -1)  # Use white (255)
            label = 2
        
        elif shape == 'rectangle':
            # Generate rectangle
            pt1 = (np.random.randint(5, 40), np.random.randint(5, 40))
            pt2 = (np.random.randint(5, 55), np.random.randint(5, 55))
            cv2.rectangle(img, pt1, pt2, 255, -1)  # Use white (255)
            label = 3
        
        elif shape == 'square':
            # Generate square
            pt1 = (np.random.randint(5, 40), np.random.randint(5, 40))
            side_length = np.random.randint(10, 25)
            pt2 = (pt1[0] + side_length, pt1[1] + side_length)
            cv2.rectangle(img, pt1, pt2, 255, -1)  # Use white (255)
            label = 4
        
        elif shape == 'triangle':
            # Generate triangle
            x1, y1 = np.random.randint(5, 55), np.random.randint(5, 55)
            x2, y2 = np.random.randint(5, 55), np.random.randint(5, 55)
            x3, y3 = np.random.randint(5, 55), np.random.randint(5, 55)
            pts = np.array([[x1, y1], [x2, y2], [x3, y3]], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.fillPoly(img, [pts], 255)  # Use white (255)
            label = 5
        
        elif shape == 'star':
            # Generate star (5-pointed)
            center = (32, 32)
            radius = 20
            pts = []
            for i in range(5):
                x = center[0] + int(radius * np.cos(i * 4 * np.pi / 5))
                y = center[1] + int(radius * np.sin(i * 4 * np.pi / 5))
                pts.append([x, y])
            pts = np.array(pts, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.fillPoly(img, [pts], 255)  # Use white (255)
            label = 6
        
        # Ensure label is set
        if label == -1:
            raise ValueError("Label was not assigned correctly.")

        # Save the image to the corresponding folder
        cv2.imwrite(os.path.join(save_dir, shape, f'{i}.png'), img)
        
        data.append(img)
        labels.append(label)

    return np.array(data).reshape(-1, img_size, img_size, 1), np.array(labels)


def read_csv(csv_path):
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []
    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)
    return path_XYs

def convert_to_image(paths_XYs, img_size=64):
    canvas = np.zeros((img_size, img_size), dtype=np.uint8)
    for XYs in paths_XYs:
        for XY in XYs:
            for i in range(len(XY) - 1):
                cv2.line(canvas, tuple(XY[i]), tuple(XY[i + 1]), 255, 1)
    return canvas

def load_data(data_dir, img_size=64, add_shape_in_folder=True):
    data = []
    labels = []
    shape_classes = ['ellipse', 'circle', 'rounded_rectangle', 'rectangle', 'square', 'triangle', 'star']

    for label, shape in enumerate(shape_classes):

        if add_shape_in_folder is True:
            shape_dir = os.path.join(data_dir, shape)
        else:
            shape_dir = data_dir

        print(f"Checking directory: {shape_dir}")  # Debug info

        if os.path.exists(shape_dir):
            for filename in os.listdir(shape_dir):
                if filename.endswith('.png'):
                    img_path = os.path.join(shape_dir, filename)
                    print(f"Found image: {img_path}")  # Debug info
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.resize(img, (img_size, img_size))
                        data.append(img)
                        labels.append(label)

    if not data:
        raise ValueError("No data found. Please check the data directory and files.")

    data = np.array(data).reshape(-1, img_size, img_size, 1)
    labels = np.array(labels)
    return data, labels



if __name__ == "__main__":
    # Generating synthetic data for training
    num_synthetic_samples = 1000  # Increase the number of synthetic samples to generate
    synthetic_data, synthetic_labels = generate_synthetic_data(num_synthetic_samples)
    print(f"Generated synthetic data shape: {synthetic_data.shape}, labels shape: {synthetic_labels.shape}")
    
    # Visualize the first 5 synthetic samples
    for i in range(5):
        plt.imshow(synthetic_data[i].reshape(64, 64), cmap='gray')
        plt.title(f"Label: {synthetic_labels[i]}")
        plt.show()
