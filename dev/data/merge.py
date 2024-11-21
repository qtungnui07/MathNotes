import os
import random
from PIL import Image

# Bố mày load folder ảnh
folder_text = 'text'  # Đường dẫn tới folder `text`

# Kiểm tra và load danh sách file ảnh
images_text = [os.path.join(folder_text, img) for img in os.listdir(folder_text) if img.endswith(('.png', '.jpg', '.jpeg'))]

# Thư mục đầu ra
output_folder = 'paragraph'  # Đường dẫn đến thư mục xuất ảnh
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Tạo 300 ảnh
for i in range(500):
    # Chọn random số ảnh từ 1 đến 5
    num_images = random.randint(1, 5)
    selected_images = random.sample(images_text, num_images)

    # Load ảnh và tính chiều cao trung bình
    images = []
    total_height = 0
    for img_path in selected_images:
        img = Image.open(img_path)
        images.append(img)
        total_height += img.height

    # Tính chiều cao trung bình
    avg_height = total_height // num_images

    # Resize các ảnh về chiều cao trung bình, giữ tỷ lệ
    resized_images = []
    for img in images:
        aspect_ratio = img.width / img.height
        new_width = int(avg_height * aspect_ratio)  # Giữ tỷ lệ chiều rộng
        resized_img = img.resize((new_width, avg_height))  # Resize ảnh
        resized_images.append(resized_img)

    # Tính tổng chiều cao với padding random giữa các ảnh
    padding_min = 0  # padding tối thiểu
    padding_max = 15  # padding tối đa
    padding_values = [random.randint(padding_min, padding_max) for _ in range(num_images - 1)]
    total_height_with_padding = sum(img.height for img in resized_images) + sum(padding_values)
    max_width = max(img.width for img in resized_images)

    # Tạo ảnh mới với chiều cao tổng hợp
    merged_image = Image.new('RGB', (max_width, total_height_with_padding), (255, 255, 255))  # nền trắng

    # Dán ảnh từng cái lên ảnh mới với padding random
    current_y = 0
    for index, img in enumerate(resized_images):
        merged_image.paste(img, (0, current_y))
        current_y += img.height
        if index < len(padding_values):  # Đảm bảo không vượt giới hạn
            current_y += padding_values[index]  # Thêm padding giữa các ảnh

    # Kiểm tra và căn chỉnh ảnh cuối cùng nếu bị thiếu chiều cao
    final_height = merged_image.height
    if current_y < final_height:
        fill_height = final_height - current_y  # Tính khoảng thiếu
        filler = Image.new('RGB', (max_width, fill_height), (255, 255, 255))  # Ảnh nền trắng
        merged_image.paste(filler, (0, current_y))  # Thêm phần trắng vào cuối

    # Lưu ảnh dưới định dạng JPEG trong thư mục paragraph
    output_path = os.path.join(output_folder, f"merged_image_{i + 1}.jpeg")
    merged_image.save(output_path, format="JPEG")

    print(f"Ảnh {i + 1} đã được lưu vào {output_path}")
