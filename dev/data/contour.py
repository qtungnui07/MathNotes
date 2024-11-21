import os
from PIL import Image
import cv2
import numpy as np

# Define the function you provided
def find_and_merge_contours(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Apply thresholding to get a binary image
    _, thresh = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Merge all contour bounding boxes
    x_min, y_min, x_max, y_max = np.inf, np.inf, -np.inf, -np.inf
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)

    # Crop the image based on the bounding box
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    
    return cropped_image

# Main function to process all images in a folder
def process_folder(input_folder, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        
        # Check if the file is an image (you can add more extensions if needed)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            # Open the image
            image = Image.open(input_path)
            
            # Apply the contour-finding and cropping function
            processed_image = find_and_merge_contours(image)
            
            # Save the processed image to the output folder in JPEG format
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpeg")
            processed_image.convert("RGB").save(output_path, "JPEG")
            print(f"Processed and saved: {output_path}")

# Define your input and output folder paths
input_folder = "raw"
output_folder = "cleaned_set"

# Run the processing function
process_folder(input_folder, output_folder)
