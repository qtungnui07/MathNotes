import os
import cv2
import random
import numpy as np
from PIL import Image
from agumentation.generatehandwritten import text_to_image
from agumentation.dilate import dilateimg
# Thư mục lưu trữ ảnh
output_folder = "text_math"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

folder_words = "con1firmed"
folder_equations = "math_1"

def downsample_image(image, scale_factor=0.5):
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    return image.resize(new_size, Image.LANCZOS)

def generate_random_sentence(file_path="txt/vocab.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        words = file.read().splitlines()
    num_words = random.randint(2, 6)
    selected_words = random.sample(words, num_words)
    sentence = ' '.join(selected_words)
    return sentence

def get_random_equation_image(folder_equations):
    equation_images = os.listdir(folder_equations)
    if not equation_images:
        print('No images found in directory:', folder_equations)
        return None
    chosen_equation = random.choice(equation_images)
    return os.path.join(folder_equations, chosen_equation)

def split_string(sentence):
    words = sentence.split()
    if len(words) < 2:
        return sentence, ""
    split_index = random.randint(1, len(words) - 1)
    part1 = ' '.join(words[:split_index])
    part2 = ' '.join(words[split_index:])
    return part1.strip(), part2.strip()

def thin_image(image_path):
    img = cv2.imread(image_path, 0)
    if img is None:
        print('Cannot open or find the image:', image_path)
        return None
    inverted_img = cv2.bitwise_not(img)
    kernel = np.ones((random.randint(2, 3), random.randint(2, 3)), np.uint8)
    img_erosion = cv2.erode(inverted_img, kernel, iterations=1)
    img_erosion = cv2.bitwise_not(img_erosion)
    return img_erosion


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

def merge_images(images):
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    result_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))
    x_offset = 0
    bounding_box = None
    for i, img in enumerate(images):
        result_image.paste(img, (x_offset, 0))
        if isinstance(img, Image.Image) and img.mode != 'RGB':
            bounding_box = {
                'x1': x_offset,
                'y1': 0,
                'x2': x_offset + img.width,
                'y2': img.height
            }
        x_offset += img.width
    return result_image, bounding_box

def main():
    for i in range(1, 1001):
        sentence = generate_random_sentence()
        part1, part2 = split_string(sentence)
        
        image1 = text_to_image(part1)
        image2 = text_to_image(part2)
        image1 = Image.fromarray(image1.astype(np.uint8))
        image2 = Image.fromarray(image2.astype(np.uint8))
        image1 = downsample_image(image1, scale_factor=0.3)
        image2 = downsample_image(image2, scale_factor=0.3)
        
        equation_path = get_random_equation_image(folder_equations)

        if equation_path is not None:
            thin_eq_image = thin_image(equation_path)
            if thin_eq_image is not None:
                equation_image = Image.fromarray(thin_eq_image)
            else:
                print("Cannot process equation image.")
                continue
        else:
            continue
        
        if random.random() < 0.5:
            image1 = dilateimg(image1)
            image2 = dilateimg(image2)
            equation_image = dilateimg(equation_image)

        position = random.choices(['start', 'middle', 'end'], weights=[10, 80, 10], k=1)[0]
        if position == 'start':
            merged_image, bbox = merge_images([equation_image, image1, image2])
        elif position == 'middle':
            merged_image, bbox = merge_images([image1, equation_image, image2])
        else:
            merged_image, bbox = merge_images([image1, image2, equation_image])

        merged_image = downsample_image(merged_image, scale_factor=0.4)

        # After merging, find contours and crop the image
        merged_image = find_and_merge_contours(merged_image)

        output_path = os.path.join(output_folder, f"text_math_{i}.jpeg")
        merged_image.save(output_path)
        print(f"Image {i} saved as '{output_path}'.")

        # Xuất tọa độ bounding box ra file txt
        if bbox:
            scale_factor = 0.4
            bbox['x1'] = int(bbox['x1'] * scale_factor)
            bbox['y1'] = int(bbox['y1'] * scale_factor)
            bbox['x2'] = int(bbox['x2'] * scale_factor)
            bbox['y2'] = int(bbox['y2'] * scale_factor)

            bbox_file = os.path.join(output_folder, f"text_math_{i}_bbox.txt")
            with open(bbox_file, 'w') as f:
                f.write(f"{bbox['x1']} {bbox['y1']} {bbox['x2']} {bbox['y2']}\n")
            print(f"Bounding box for Image {i} saved as '{bbox_file}'.")

if __name__ == "__main__":
    main()
