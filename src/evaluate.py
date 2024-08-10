import os
import numpy as np
import cv2
from src.model import load_trained_model
from src.data_preparation.data_preparation import read_csv

def regularize_curve(XYs):
    for i in range(len(XYs)):
        XY = np.array(XYs[i], dtype=np.float32)
        if XY.ndim == 1:
            XY = XY.reshape(-1, 2)
        elif XY.ndim == 2 and XY.shape[1] != 2:
            XY = XY.reshape(-1, 2)
        if len(XY) < 3:
            print(f"Warning: Not enough points to regularize curve {i}.")
            continue
        epsilon = 1.5
        approx = cv2.approxPolyDP(XY, epsilon, closed=True)
        XYs[i] = approx
    return XYs

def symmetrize_curve(XYs):
    for i in range(len(XYs)):
        XY = XYs[i]
        max_x = np.max(XY[:, 0])
        mirrored_XY = XY.copy()
        mirrored_XY[:, 0] = max_x - (XY[:, 0] - max_x)
        XYs[i] = np.vstack([XY, mirrored_XY])
    return XYs

def complete_curve(XYs):
    for i in range(len(XYs)):
        XY = np.array(XYs[i], dtype=np.float32)
        if XY.ndim == 1:
            XY = XY.reshape(-1, 2)
        elif XY.ndim == 3:
            XY = XY.squeeze()
        if XY.shape[0] > 0:
            XYs[i] = np.vstack([XY, XY[0]])
        else:
            print(f"Warning: Curve {i} is empty or invalid.")
    return XYs

def apply_color_border(img):
    border_size = 5
    color = (255, 0, 0)
    img_with_border = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=color)
    return img_with_border

def convert_to_image(paths_XYs, img_size=(256, 256)):
    canvas = np.zeros((img_size[1], img_size[0]), dtype=np.uint8)
    for XY in paths_XYs:
        for i in range(len(XY) - 1):
            cv2.line(canvas, tuple(XY[i]), tuple(XY[i + 1]), 255, 1)
    return canvas

def predict_and_save(input_csv, output_png):
    try:
        # Read and preprocess data
        paths_XYs = read_csv(input_csv)
        if not paths_XYs:
            raise ValueError("No data found in CSV file.")

        # Process each curve: regularize, symmetrize, and complete
        for i in range(len(paths_XYs)):
            paths_XYs[i] = regularize_curve(paths_XYs[i])
            paths_XYs[i] = symmetrize_curve(paths_XYs[i])
            paths_XYs[i] = complete_curve(paths_XYs[i])

        # Convert processed curves to image
        img_size = (256, 256)
        img = convert_to_image(paths_XYs, img_size=img_size)
        img = apply_color_border(img)

        # Save the final image
        cv2.imwrite(output_png, img)
        print(f"Output saved as {output_png}")

    except Exception as e:
        print(f"Error in predict_and_save: {e}")

if __name__ == "__main__":
    input_csv = 'data/problems/frag0.csv'
    output_png = 'output_image.png'
    predict_and_save(input_csv, output_png)
