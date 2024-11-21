import os
import random
import numpy as np
from PIL import Image
from tqdm import tqdm
import onnx
import onnxruntime as ort
from straug.warp import Distort, Stretch
from straug.geometry import Perspective, Shrink
from torchvision import transforms
import torch
# Thiết lập các phép biến đổi cho hình ảnh
resize_transform = transforms.Resize((224, 224))
to_tensor_transform = transforms.ToTensor()

def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Mỗi đoạn cách nhau bởi dòng trống
        paragraphs = content.split('\n')
        return [para.strip() for para in paragraphs if para.strip()]

def create_dir(directory):
    os.makedirs(directory, exist_ok=True)



def invert_image(image):
    return Image.fromarray(255 - np.array(image))

def apply_random_distortion(image):
    distortions = [None, Distort(), Stretch(), Perspective(), Shrink()]
    probabilities = [0.3, 0.2, 0.15, 0.15, 0.1]
    
    chosen_distortion = random.choices(distortions, probabilities)[0]
    
    if chosen_distortion:
        return chosen_distortion(image, mag=3)
    return image

def augment_word_image(image):
    image = invert_image(image)
    image = apply_random_distortion(image)
    return invert_image(image)

def process_image(img_path):
    try:
        with Image.open(img_path) as img:
            original_size = img.size
            augmented_image = augment_word_image(img)
            resized_img = resize_transform(augmented_image)
            tensor_img = to_tensor_transform(resized_img).unsqueeze(0)
        return tensor_img, original_size
    except Exception as e:
        print(f"Error processing image {img_path}: {str(e)}")
        return None, None

def adjust_y(predicted_y, original_height, resized_height=224):
    if predicted_y < 0 or predicted_y > resized_height:
        print(f"Giá trị y dự đoán không hợp lệ: {predicted_y}")
        predicted_y = max(0, min(predicted_y, resized_height))
    adjusted_y = predicted_y * (original_height / resized_height)
    return adjusted_y

def predict_y(onnx_session, image_tensor, original_size):
    image_tensor = image_tensor.numpy().astype(np.float16)  # Chuyển đổi tensor sang numpy array với kiểu float16
    # Dự đoán với mô hình ONNX
    inputs = {onnx_session.get_inputs()[0].name: image_tensor}
    predicted_y = onnx_session.run(None, inputs)[0].squeeze()
    adjusted_y = adjust_y(predicted_y, original_size[1])
    return adjusted_y

def get_images_for_sentence(sentence, folder_path='con1firmed'):
    words = sentence.split()
    word_images = []
    
    for word in words:
        # Nếu từ là "con", dùng folder "con1"
        if word.strip().lower() == 'con':
            word_folder = os.path.join(folder_path, 'con1')
        else:
            word_folder = os.path.join(folder_path, word)
        
        # Kiểm tra xem folder có tồn tại không
        if os.path.isdir(word_folder):
            # Lấy danh sách ảnh có định dạng '.jpeg'
            images = [img for img in os.listdir(word_folder) if img.endswith('.jpeg')]
            if images:
                chosen_image = random.choice(images)  # Chọn ngẫu nhiên một ảnh
                word_images.append((word, chosen_image))
    
    return word_images

def stitch_images(image_data, spacing=35):
    if not image_data:
        return None

    baseline_y = max(y for _, y in image_data)
    canvas_height = baseline_y * 2
    total_width = sum(Image.open(img_path).width for img_path, _ in image_data) + spacing * (len(image_data) - 1)
    
    canvas = Image.new("RGB", (total_width, canvas_height), "white")
    current_x = 0

    for img_path, y in image_data:
        img = Image.open(img_path)
        offset = baseline_y - y
        canvas.paste(img, (current_x, offset))
        current_x += img.width + spacing

    return canvas

def text_to_image(text):
    # Đọc đoạn từ input text
    sentences = [text]
    
    # Folder để lưu kết quả

    onnx_model_path = 'model.onnx'
    
    # Khởi tạo session ONNX Runtime
    if os.path.exists(onnx_model_path):
        onnx_session = ort.InferenceSession(onnx_model_path)
    else:
        print(f"Không tìm thấy mô hình ONNX tại {onnx_model_path}")
        return None

    image_data = []
    with torch.no_grad():
        for idx, sentence in enumerate(tqdm(sentences, desc="Processing Paragraph")):
            if sentence.strip():
                word_images = get_images_for_sentence(sentence)
                y_coords = []
                image_paths = []
                
                for word, img_name in word_images:
                    img_path = os.path.join('con1firmed', word, img_name)
                    image_tensor, original_size = process_image(img_path)
                    
                    if image_tensor is not None:
                        y = int(predict_y(onnx_session, image_tensor, original_size))
                        y_coords.append(y)
                        image_paths.append(img_path)

                if image_paths:
                    image_data = list(zip(image_paths, y_coords))
                    final_image = stitch_images(image_data)
                    
                    # Convert PIL Image to numpy array
                    return np.array(final_image)
                else:
                    print(f"Không có ảnh để ghép cho đoạn: {sentence}")

    return None

