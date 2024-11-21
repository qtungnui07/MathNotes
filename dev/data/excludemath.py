import os
import random
from augmentation.generatehandwritten import text_to_image
from PIL import Image

import cv2
import numpy as np
def downsample_image(image, scale_factor=0.5):
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    return image.resize(new_size, Image.LANCZOS)
# Đọc các từ từ file vocab.txt
def read_vocab(vocab_file):
    with open(vocab_file, 'r',encoding='utf-8') as f:
        words = [line.strip() for line in f.readlines()]
    return words
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

# Tạo câu ngẫu nhiên từ danh sách từ
def generate_random_sentence(words, min_length=random.randint(1,2), max_length=5):
    num_words = random.randint(min_length, max_length)
    sentence = ' '.join(random.sample(words, num_words))
    return sentence

# Tạo thư mục "text" nếu chưa tồn tại
output_folder = "text"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Đọc từ trong vocab.txt
vocab_file = 'vocab.txt'  # Đảm bảo file này có sẵn trong thư mục làm việc
words = read_vocab(vocab_file)

# Số lượng ảnh cần tạo
num_images = 1000  # Ví dụ: tạo 200 ảnh

# Tạo và lưu ảnh vào thư mục
for i in range(num_images):
    # Tạo câu ngẫu nhiên từ từ vựng
    sentence = generate_random_sentence(words)
    
    # Tạo ảnh từ câu
    image = text_to_image(sentence)

    # Lưu ảnh vào thư mục
    image_path = os.path.join(output_folder, f"image_{i+1}.png")
    img = Image.fromarray(image)

    img = find_and_merge_contours(img)
    img = downsample_image(img,scale_factor=0.3)


    img.save(image_path)

    # In ra thông báo mỗi lần lưu ảnh
    print(f"Đã lưu ảnh {image_path}")
