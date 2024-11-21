import random
import os
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import cv2

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

def downsample_image(image, scale_factor=0.5):
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    return image.resize(new_size, Image.LANCZOS)

# Các hàm augmentation
def apply_rotation(image):
    angle = random.uniform(0, 360)
    return image.rotate(angle, expand=True, fillcolor=(255, 255, 255))

def apply_flipping(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)



def apply_cutout(image):
    width, height = image.size
    cutout_size = (random.randint(10, 30), random.randint(10, 30))
    cutout_position = (random.randint(0, width - cutout_size[0]), random.randint(0, height - cutout_size[1]))
    image_np = np.array(image)
    image_np[cutout_position[1]:cutout_position[1] + cutout_size[1], cutout_position[0]:cutout_position[0] + cutout_size[0]] = (255, 255, 255)
    return Image.fromarray(image_np)

def augment_image(image):
    augmentations = [apply_rotation, apply_flipping, apply_cutout]
    random.shuffle(augmentations)
    for aug in augmentations:
        if random.random() < 0.5:  # Xác suất 50%
            image = aug(image)
    return image

# Tạo 10 ảnh biến đổi từ mỗi ảnh trong cleaned_geometry
def generate_augmented_images(input_folder, output_folder, num_images=10):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".jpeg") or filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path).convert("RGB")
            image = find_and_merge_contours(image)
            image = downsample_image(image)

            for i in range(num_images):
            
                augmented_image = augment_image(image)
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_aug_{i+1}.jpg")
                augmented_image = find_and_merge_contours(augmented_image)
                augmented_image.save(output_path, "JPEG")
                print(f"Đã lưu ảnh biến đổi tại {output_path}")

# Đường dẫn đến thư mục ảnh gốc và thư mục lưu ảnh biến đổi
input_folder = "cleaned_geometry"
output_folder = "augmented_geometry"

# Gọi hàm để tạo ảnh biến đổi
generate_augmented_images(input_folder, output_folder)
