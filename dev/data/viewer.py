import cv2
import os
import numpy as np
from pathlib import Path

def draw_bounding_boxes(image, labels, class_names):
    """
    Draw bounding boxes on the image based on YOLO label file.
    
    Parameters:
    - image: The image to draw bounding boxes on.
    - labels: List of labels in YOLO format.
    - class_names: List of class names corresponding to class IDs.
    """
    h, w, _ = image.shape
    for label in labels:
        class_id, center_x, center_y, width, height = map(float, label.split())
        
        # Convert from normalized coordinates to pixel values
        x1 = int((center_x - width / 2) * w)
        y1 = int((center_y - height / 2) * h)
        x2 = int((center_x + width / 2) * w)
        y2 = int((center_y + height / 2) * h)
        
        # Draw bounding box
        color = (0, 255, 0)  # Green color for the box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Put the label with class name
        label_text = class_names[int(class_id)]
        cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image

def load_labels(label_file):
    """
    Load labels from the YOLO format text file.
    
    Parameters:
    - label_file: Path to the YOLO label file.
    
    Returns:
    - A list of label lines.
    """
    with open(label_file, 'r') as f:
        return f.readlines()

def show_yolo_dataset(dataset_dir, class_names):
    """
    Function to display the YOLO dataset images with bounding boxes.
    
    Parameters:
    - dataset_dir: Path to the directory containing images and label files.
    - class_names: List of class names.
    """
    image_dir = Path(dataset_dir) / 'images' / 'train'
    label_dir = Path(dataset_dir) / 'labels' / 'train'
    
    # Get all image files
    image_files = list(image_dir.glob('*.jpg'))
    
    for img_path in image_files:
        # Load the image
        image = cv2.imread(str(img_path))
        
        # Get corresponding label file
        label_path = label_dir / f'{img_path.stem}.txt'
        
        if label_path.exists():
            # Load labels from YOLO format
            labels = load_labels(label_path)
            
            # Draw bounding boxes on the image
            image = draw_bounding_boxes(image, labels, class_names)
        
        # Show the image with bounding boxes
        cv2.imshow(f'Image: {img_path.name}', image)
        
        # Wait until a key is pressed to move to the next image
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
    
    # Close all windows after displaying the images
    cv2.destroyAllWindows()

def main():
    dataset_dir = "test_yolo"  # Thư mục chứa dataset YOLO
    class_names = ['text', 'math','geometry']  # Danh sách tên lớp
    
    show_yolo_dataset(dataset_dir, class_names)

if __name__ == "__main__":
    main()
