from PIL import Image
import cv2
import numpy as np
import os
import random

def create_canvas():
    return Image.new('RGB', (640, 640), (255, 255, 255))

def read_bounding_boxes(txt_path):
    boxes = []
    with open(txt_path, 'r') as file:
        for line in file:
            # Chuyển mỗi dòng thành list các số
            coords = list(map(int, line.strip().split()))
            boxes.append(coords)
    return boxes

def get_content_bbox_using_contours(image):
    """Tính toán bounding box bao quanh tất cả các phần có nội dung trong ảnh bằng contours"""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    x, y, w, h = cv2.boundingRect(np.concatenate(contours))
    return [x, y, x + w, y + h]

def place_image_and_adjust_boxes(canvas, image, boxes):
    canvas_width, canvas_height = canvas.size
    img_width, img_height = image.size
    scale = 1
    
    while img_width > canvas_width or img_height > canvas_height:
        image = image.resize((img_width // 2, img_height // 2), Image.LANCZOS)
        img_width, img_height = image.size
        scale *= 2
        boxes = [[x//scale for x in box] for box in boxes]
    
    max_x = canvas_width - img_width
    max_y = canvas_height - img_height
    
    if max_x < 0 or max_y < 0:
        raise ValueError("Kích thước ảnh quá lớn để ghép vào canvas")
    
    offset_x = random.randint(0, max_x)
    offset_y = random.randint(0, max_y)
    canvas.paste(image, (offset_x, offset_y))
    
    adjusted_boxes = []
    for box in boxes:
        adjusted_box = [
            box[0] + offset_x,
            box[1] + offset_y,
            box[2] + offset_x,
            box[3] + offset_y
        ]
        adjusted_boxes.append(adjusted_box)
    
    content_bbox = get_content_bbox_using_contours(image)
    
    if content_bbox:
        content_bbox = [
            content_bbox[0] + offset_x,
            content_bbox[1] + offset_y,
            content_bbox[2] + offset_x,
            content_bbox[3] + offset_y
        ]
    
    return canvas, adjusted_boxes, content_bbox

def save_bounding_boxes_to_txt(overall_bbox, boxes, file_path):
    with open(file_path, 'w') as file:
        file.write(f"text {' '.join(map(str, overall_bbox))}\n")
        for box in boxes:
            file.write(f"math {' '.join(map(str, box))}\n")

def main():
    input_folder = 'paragraph_math'
    output_folder = 'format_math'
    os.makedirs(output_folder, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    for i, img_file in enumerate(image_files, 1):
        img_path = os.path.join(input_folder, img_file)
        txt_path = os.path.join(input_folder, os.path.splitext(img_file)[0] + '.txt')
        
        if not os.path.exists(txt_path):
            print(f"Không tìm thấy file txt cho ảnh {img_file}")
            continue
        
        image = Image.open(img_path)
        boxes = read_bounding_boxes(txt_path)
        
        canvas = create_canvas()
        try:
            canvas, adjusted_boxes, content_bbox = place_image_and_adjust_boxes(canvas, image, boxes)
            output_img_path = os.path.join(output_folder, f'{i}.jpeg')
            output_txt_path = os.path.join(output_folder, f'{i}.txt')
            canvas.save(output_img_path)
            save_bounding_boxes_to_txt(content_bbox, adjusted_boxes, output_txt_path)
        except Exception as e:
            print(f"Lỗi khi xử lý ảnh {img_file}: {str(e)}")

if __name__ == "__main__":
    main()
    print("Quá trình xử lý hoàn tất.")
