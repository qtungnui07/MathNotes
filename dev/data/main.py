import os
import random
from PIL import Image
from augmentation.create_background import create_random_canvas
from augmentation.contour import find_and_merge_contours
from augmentation.dilate import dilateimg, draw_dots, draw_lines, draw_smooth_random_curves, invert_image_colors

# Hàm kiểm tra sự trùng lặp giữa các ảnh đã được đặt
def is_overlapping(new_position, new_size, placed_images):
    x1, y1 = new_position
    w1, h1 = new_size
    for (px, py, pw, ph) in placed_images:
        if (x1 < px + pw and x1 + w1 > px and y1 < py + ph and y1 + h1 > py):
            return True
    return False

# Hàm loại bỏ nền trắng
def remove_white_background(img):
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

# Hàm điều chỉnh tọa độ của bounding box sau khi thay đổi kích thước ảnh
def adjust_bbox_coordinates(bbox, original_bbox, new_pos, scale_factors):
    x1, y1, x2, y2 = bbox
    crop_x_min, crop_y_min, crop_x_max, crop_y_max = original_bbox
    new_x, new_y = new_pos
    scale_x, scale_y = scale_factors
    
    relative_x1 = x1 - crop_x_min
    relative_y1 = y1 - crop_y_min
    relative_x2 = x2 - crop_x_min
    relative_y2 = y2 - crop_y_min
    
    final_x1 = new_x + (relative_x1 * scale_x)
    final_y1 = new_y + (relative_y1 * scale_y)
    final_x2 = new_x + (relative_x2 * scale_x)
    final_y2 = new_y + (relative_y2 * scale_y)
    
    return (int(final_x1), int(final_y1), int(final_x2), int(final_y2))
def get_folder_label(image_path, folder_label_mapping):
    # Get the parent folder name from the image path
    parent_folder = os.path.basename(os.path.dirname(image_path))
    # Return the mapped label for this folder
    return folder_label_mapping.get(parent_folder, 'text')  # Default to 'text' if mapping not found
def balance_labels(label_counts, total_images, current_image_label, target_percentages={'text': 34, 'math': 33, 'geometry': 33}):
    """
    Determine if we should use this image based on its label and current distribution
    Returns: Boolean indicating if we should use this image
    """
    # Calculate total images processed so far
    current_total = sum(label_counts.values())
    if current_total == 0:
        return True
        
    # Calculate current percentages
    current_percentages = {
        label: (count / current_total * 100) if current_total > 0 else 0
        for label, count in label_counts.items()
    }
    
    # If this label is already exceeding its target percentage, reject it
    if current_percentages.get(current_image_label, 0) > target_percentages[current_image_label]:
        return False
        
    # Calculate how far each label is from its target
    label_gaps = {
        label: target_percentages[label] - current_percentages.get(label, 0)
        for label in target_percentages
    }
    
    # Prioritize labels that are furthest below their target
    max_gap_label = max(label_gaps, key=label_gaps.get)
    if current_image_label == max_gap_label:
        return True
    
    # Allow some randomness to prevent strict ordering
    if random.random() < 0.3:  # 30% chance to accept even if not the most needed label
        return True
        
    return False

def generate_image_and_labels(output_dir, image_index, label_counts, total_images=350):
    canvas_size = 640
    canvas = create_random_canvas()
    
    main_folder = 'datasets_test'
    
    folder_label_mapping = {
        'augmented_geometry': 'geometry',
        'math': 'math',
        'meth': 'math',
        'paragraph': 'text',
        'text': 'text'
    }
    
    subfolders = [os.path.join(main_folder, subfolder) for subfolder in os.listdir(main_folder) 
                  if os.path.isdir(os.path.join(main_folder, subfolder))]
    
    placed_images = []
    bounding_boxes = []
    
    # Get all images and their labels
    all_images_with_labels = []
    for folder in subfolders:
        images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith((".png", ".jpg", ".jpeg"))]
        for img_path in images:
            label = get_folder_label(img_path, folder_label_mapping)
            all_images_with_labels.append((img_path, label))
    
    # Shuffle the images
    random.shuffle(all_images_with_labels)
    
    # Determine which labels need more representation
    current_total = sum(label_counts.values())
    if current_total > 0:
        current_percentages = {
            label: (count / current_total * 100)
            for label, count in label_counts.items()
        }
        target_percentages = {'text': 34, 'math': 33, 'geometry': 33}
        needed_labels = sorted(
            target_percentages.keys(),
            key=lambda x: target_percentages[x] - current_percentages.get(x, 0),
            reverse=True
        )
    else:
        needed_labels = ['text', 'math', 'geometry']
    
    # Number of images to try to place (1-3)
    num_images_to_try = random.randint(1, 5)
    
    # Try to place images while maintaining label balance
    images_placed = 0
    attempts = 0
    max_attempts = len(all_images_with_labels)  # Prevent infinite loop
    
    while images_placed < num_images_to_try and attempts < max_attempts:
        attempts += 1
        
        # Prioritize needed labels
        for needed_label in needed_labels:
            candidate_images = [(img, label) for img, label in all_images_with_labels if label == needed_label]
            if candidate_images:
                img_path, label = random.choice(candidate_images)
                
                # Check if adding this image would maintain label balance
                if not balance_labels(label_counts, total_images, label):
                    continue
                
                # Rest of the image processing code remains the same
                img = Image.open(img_path).convert("RGBA")
                if random.random() < 0.5:
                    img = dilateimg(img)
                img_with_bbox = find_and_merge_contours(img)
                img, original_bbox = img_with_bbox
                img = remove_white_background(img)
                
                min_size = 169
                max_size = 640
                new_size = random.randint(min_size, max_size)
                img.thumbnail((new_size, new_size))
                img_w, img_h = img.size
                
                # Try to place the image without overlap
                placement_attempts = 50
                for _ in range(placement_attempts):
                    x = random.randint(0, canvas_size - img_w)
                    y = random.randint(0, canvas_size - img_h)
                    
                    if not is_overlapping((x, y), (img_w, img_h), placed_images):
                        placed_images.append((x, y, img_w, img_h))
                        canvas.paste(img, (x, y), img)
                        
                        label_counts[label] = label_counts.get(label, 0) + 1
                        bounding_boxes.append(f"{label} {x} {y} {x + img_w} {y + img_h}")
                        images_placed += 1
                        break
                
                if images_placed >= num_images_to_try:
                    break
    
    # Save the image and bounding boxes
    image_filename = f"image_{image_index:04d}.jpg"
    txt_filename = f"image_{image_index:04d}.txt"
    
    image_path = os.path.join(output_dir, "images", image_filename)
    txt_path = os.path.join(output_dir, "labels", txt_filename)
    
    canvas = canvas.convert("RGB")
    canvas = augment_image(canvas)
    canvas.save(image_path, "JPEG")
    
    with open(txt_path, 'w') as f:
        f.write('\n'.join(bounding_boxes))

def augment_image(image):
    augmentations = [draw_dots, draw_smooth_random_curves, draw_lines,invert_image_colors]
    random.shuffle(augmentations)
    for aug in augmentations:
        if random.random() < 0.4:  # Xác suất 50%
            image = aug(image)
    
    return image

def main():
    output_dir = "test"
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "labels"), exist_ok=True)
    
    label_counts = {'text': 0, 'math': 0, 'geometry': 0}
    total_images = 500
    
    for i in range(total_images):
        generate_image_and_labels(output_dir, i, label_counts, total_images)
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} images")
            print(f"Current label distribution: {label_counts}")
    
    # Save final label counts
    with open(os.path.join(output_dir, 'label_counts.txt'), 'w') as f:
        for label, count in label_counts.items():
            f.write(f"{label}: {count}\n")

if __name__ == "__main__":
    main()
