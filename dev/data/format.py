from PIL import Image, ImageDraw
import os
import random

# Hàm để tạo canvas trắng
def create_canvas():
    canvas = Image.new('RGB', (640, 640), (255, 255, 255))  # canvas 640x640 màu trắng
    return canvas

# Hàm để ghép ảnh vào canvas tại vị trí ngẫu nhiên, không chạm biên
def place_image_on_canvas(canvas, image):
    canvas_width, canvas_height = canvas.size
    img_width, img_height = image.size

    # Kiểm tra nếu ảnh quá lớn so với canvas
    if img_width > canvas_width or img_height > canvas_height:
        image = image.resize((img_width // 2, img_height // 2), Image.LANCZOS)
        img_width, img_height = image.size

    max_x = canvas_width - img_width
    max_y = canvas_height - img_height
    
    if max_x < 0 or max_y < 0:
        raise ValueError("Kích thước ảnh quá lớn để ghép vào canvas")
    
    # Chọn vị trí ngẫu nhiên (x, y) trong phạm vi cho phép
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)
    
    # Dán ảnh vào vị trí (x, y) trên canvas
    canvas.paste(image, (x, y))
    return canvas, (x, y, x + img_width, y + img_height)

# Hàm để lưu thông tin bounding box vào file .txt
def save_bounding_box_to_txt(bbox, file_path):
    with open(file_path, 'a') as file:
        file.write(f"text {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")

# Đường dẫn đến thư mục chứa ảnh
folder = 'paragraph'  # Đảm bảo thư mục chứa ảnh tồn tại và có các ảnh

# Tạo thư mục để lưu kết quả
output_folder = 'format_paragraph'
os.makedirs(output_folder, exist_ok=True)

# Danh sách các ảnh trong thư mục
image_files = os.listdir(folder)
total_images = len(image_files)

# Kiểm tra nếu thư mục không có ảnh nào
if total_images == 0:
    raise ValueError("Thư mục 'paragraph' không có ảnh nào để xử lý.")

# Tạo 300 ảnh và lưu bounding box vào file .txt
for i in range(1, 301):  # Chạy từ 1 đến 300
    # Tạo canvas trắng
    canvas = create_canvas()
    
    # Chọn ảnh lần lượt từ danh sách, khi hết sẽ quay lại từ đầu
    image_path = os.path.join(folder, image_files[(i - 1) % total_images])
    image = Image.open(image_path)
    
    # Đặt ảnh vào canvas và lấy thông tin bounding box
    canvas, bbox = place_image_on_canvas(canvas, image)
    
    # Đường dẫn ảnh kết quả
    image_path = os.path.join(output_folder, f'{i}.jpeg')
    canvas.save(image_path)
    
    # Đường dẫn file bounding box
    txt_path = os.path.join(output_folder, f'{i}.txt')
    save_bounding_box_to_txt(bbox, txt_path)

print("Quá trình tạo 300 ảnh hoàn tất và thông tin bounding box đã được lưu.")
