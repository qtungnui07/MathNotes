import os
import random
from PIL import Image

# Bước 1: Tạo hàm để đọc bounding box từ file txt
def read_bounding_boxes(file_path):
    with open(file_path, 'r') as file:
        boxes = []
        for line in file:
            x1, y1, x2, y2 = map(int, line.strip().split())
            boxes.append((x1, y1, x2, y2))
    return boxes

# Bước 2: Tạo hàm để ghi bounding box vào file txt
def write_bounding_boxes(file_path, boxes):
    with open(file_path, 'w') as file:
        for (x1, y1, x2, y2) in boxes:
            file.write(f"{x1} {y1} {x2} {y2}\n")

# Bước 3: Hàm chính để merge ảnh và tạo 300 ảnh ngẫu nhiên
def create_and_merge_images(folder_path, output_folder, num_images=300):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Lấy danh sách các ảnh có sẵn
    images = [f for f in os.listdir(folder_path) if f.endswith('.jpeg')]
    
    if len(images) == 0:
        print("Không có ảnh nào trong thư mục.")
        return

    # Tạo 300 ảnh ngẫu nhiên và gộp chúng lại
    for i in range(num_images):
        # Giới hạn số ảnh tối đa là số ảnh có sẵn
        num_to_merge = random.randint(1, 6)  # Mỗi lần gộp từ 1 đến 6 ảnh
        selected_images = random.sample(images, num_to_merge)
        
        total_height = 0
        max_width = 0
        merged_boxes = []
        y_offset = 0
        
        images_to_merge = []
        
        for img_name in selected_images:
            img_path = os.path.join(folder_path, img_name)
            txt_path = os.path.join(folder_path, img_name.replace('.jpeg', '_bbox.txt'))
            
            # Kiểm tra file bounding box
            if not os.path.exists(txt_path):
                print(f"File bounding box không tồn tại cho ảnh {img_name}. Bỏ qua ảnh này.")
                continue
            
            img = Image.open(img_path)
            width, height = img.size
            images_to_merge.append(img)
            
            # Cập nhật kích thước và bounding box
            total_height += height
            max_width = max(max_width, width)
            
            # Đọc bounding box và điều chỉnh theo y_offset
            boxes = read_bounding_boxes(txt_path)
            for (x1, y1, x2, y2) in boxes:
                new_box = (x1, y1 + y_offset, x2, y2 + y_offset)
                merged_boxes.append(new_box)
            
            y_offset += height
        
        # Tạo ảnh mới với kích thước tổng hợp
        merged_image = Image.new('RGB', (max_width, total_height), "white")
        y_offset = 0
        for img in images_to_merge:
            merged_image.paste(img, (0, y_offset))
            y_offset += img.size[1]
        
        # Lưu ảnh đã merge và bounding box vào thư mục mới
        output_image_path = os.path.join(output_folder, f"{i+1}.jpeg")
        output_txt_path = os.path.join(output_folder, f"{i+1}.txt")
        
        merged_image.save(output_image_path)
        write_bounding_boxes(output_txt_path, merged_boxes)
        print(f"Đã tạo ảnh {i+1} và lưu vào {output_image_path}.")

# Đường dẫn tới thư mục chứa ảnh gốc
folder_path = 'text_math'  # Thư mục chứa ảnh có sẵn và bounding boxes

# Thư mục đầu ra để lưu ảnh đã tạo
output_folder = 'paragraph_math'  # Thư mục chứa ảnh kết quả

# Gọi hàm để tạo 300 ảnh ngẫu nhiên
create_and_merge_images(folder_path, output_folder, num_images=300)
