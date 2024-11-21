import random
from PIL import Image, ImageDraw

def create_random_canvas():
    # Kích thước canvas
    width, height = 640, 640

    # Xác suất random canvas kiểu nào, làm hẳn một cái dict
    canvas_type = random.choices(
        ['white', 'grid', 'diagonal', 'vertical','lines'],
        weights=[20,20,20,20,20]
    )[0]

    # Khởi tạo một canvas trắng
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    if canvas_type == 'grid':
        # Vẽ grid, chọn một kích thước ô ngẫu nhiên từ 10 đến 50 pixel
        grid_size = random.randint(35, 50)
        for x in range(0, width, grid_size):
            draw.line([(x, 0), (x, height)], fill='black')
        for y in range(0, height, grid_size):
            draw.line([(0, y), (width, y)], fill='black')
            
    elif canvas_type == 'diagonal':
        # Vẽ các đường chéo cách nhau một khoảng ngẫu nhiên từ 20 đến 40 pixel
        spacing = random.randint(20, 40)
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x - height, height)], fill='black')
            draw.line([(x, height), (x + height, 0)], fill='black')


    elif canvas_type == 'vertical':
            spacing = random.randint(20, 40)
            for x in range(0, width, spacing):
                draw.line([(x, 0), (x, height)], fill='black')  
    elif canvas_type== 'lines':
            num_lines = random.randint(15,25)
            line_spacing = height // (num_lines + 1)

            # Vẽ các đường ngang
            for i in range(1, num_lines + 1):
                y_position = i * line_spacing
                draw.line((0, y_position, width, y_position), fill='black', width=1)
    
    # Tạo các chấm đen ngẫu nhiên

    # Trả về đối tượng Image
    return img
