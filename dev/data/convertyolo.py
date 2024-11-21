import os
import shutil
from pathlib import Path

def convert_to_yolo_format(x1, y1, x2, y2, img_width, img_height):
    """
    Convert bounding box coordinates from (x1,y1,x2,y2) to YOLO format (center_x, center_y, width, height)
    All values are normalized to [0,1]
    """
    # Calculate width and height of the box
    box_width = x2 - x1
    box_height = y2 - y1
    
    # Calculate center coordinates
    center_x = x1 + box_width/2
    center_y = y1 + box_height/2
    
    # Normalize values
    center_x /= img_width
    center_y /= img_height
    box_width /= img_width
    box_height /= img_height
    
    return center_x, center_y, box_width, box_height

def create_yolo_dataset(input_dir, output_dir):
    """
    Convert dataset to YOLO format (only training data).
    """
    # Create output directories for images and labels
    output_dir = Path(output_dir)
    (output_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)

    # Create class mapping
    class_mapping = {
        'text': 0,
        'math': 1,
        'geometry': 2
    }
    
    # Save class mapping to classes.txt
    with open(output_dir / 'classes.txt', 'w') as f:
        for class_name in class_mapping:
            f.write(f'{class_name}\n')
    
    # Get list of all images
    input_dir = Path(input_dir)
    image_files = list((input_dir / 'images').glob('*.jpg'))
    total_images = len(image_files)
    
    # Create data.yaml
    yaml_content = f"""
path: {output_dir.absolute()}
train: images/train

nc: {len(class_mapping)}  # number of classes
names: {list(class_mapping.keys())}  # class names
    """
    
    with open(output_dir / 'data.yaml', 'w') as f:
        f.write(yaml_content.strip())
    
    # Process each image and its corresponding label file
    for idx, img_path in enumerate(image_files):
        # Only use the training set (no validation)
        subset = 'train'
        
        # Get corresponding label file
        label_path = input_dir / 'labels' / f'{img_path.stem}.txt'
        
        if not label_path.exists():
            print(f"Warning: No label file found for {img_path.name}")
            continue
        
        # Copy image to training directory
        shutil.copy(str(img_path), 
                   str(output_dir / 'images' / subset / img_path.name))
        
        # Convert label file to YOLO format
        img_width = 640  # Assuming all images are 640x640
        img_height = 640
        
        yolo_lines = []
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    print(f"Warning: Invalid line in {label_path}: {line}")
                    continue
                    
                class_name = parts[0]
                if class_name not in class_mapping:
                    print(f"Warning: Unknown class {class_name} in {label_path}")
                    continue
                    
                class_id = class_mapping[class_name]
                x1, y1, x2, y2 = map(float, parts[1:])
                
                # Convert to YOLO format
                center_x, center_y, width, height = convert_to_yolo_format(
                    x1, y1, x2, y2, img_width, img_height)
                
                # Create YOLO format line: <class_id> <center_x> <center_y> <width> <height>
                yolo_line = f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}"
                yolo_lines.append(yolo_line)
        
        # Save YOLO format labels
        with open(output_dir / 'labels' / subset / f'{img_path.stem}.txt', 'w') as f:
            f.write('\n'.join(yolo_lines))
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{total_images} images")

def main():
    input_dir = "test"  # Thư mục chứa test gốc
    output_dir = "test_yolo"  # Thư mục output cho format YOLO
    
    create_yolo_dataset(input_dir, output_dir)
    print("Dataset conversion completed!")
    
    # Print dataset statistics
    train_images = len(list((Path(output_dir) / 'images' / 'train').glob('*.jpg')))
    
    print("\nDataset Statistics:")
    print(f"Total images: {train_images}")
    print(f"Training images: {train_images}")

if __name__ == "__main__":
    main()
