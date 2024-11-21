import cv2
import numpy as np
from PIL import Image,ImageDraw
import random
from PIL import Image, ImageOps

def invert_image_colors(image):
    """
    Hàm để đảo ngược màu của ảnh PIL.
    
    Parameters:
    - image (PIL.Image): Ảnh PIL đầu vào
    
    Returns:
    - PIL.Image: Ảnh sau khi đảo ngược màu
    """
    # Đảo ngược màu ảnh
    inverted_image = ImageOps.invert(image.convert("RGB"))
    return inverted_image
def dilateimg(img_pil: Image.Image) -> Image.Image:
    """
    Hàm xử lý ảnh PIL, biến đổi ảnh gốc thành ảnh nhị phân với các bước nghịch đảo và giãn nở.
    
    Parameters:
        img_pil (Image.Image): Ảnh đầu vào dạng PIL Image (grayscale).
        
    Returns:
        Image.Image: Ảnh kết quả sau khi xử lý, dạng PIL Image.
    """
    # Chuyển ảnh PIL sang numpy array
    img = np.array(img_pil)

    # Bước 1: Nghịch đảo ảnh đầu vào
    img_inverted = cv2.bitwise_not(img)

    # Bước 2: Chuyển ảnh nghịch đảo thành nhị phân
    _, binary_result = cv2.threshold(img_inverted, 50, 255, cv2.THRESH_BINARY)

    # Bước 3: Tạo kernel để làm giãn nở
    kernel = np.ones((random.randint(1,3),random.randint(1,3)), np.uint8)  # Điều chỉnh kích thước kernel nếu cần

    # Bước 4: Giãn nở vùng trắng (ảnh nghịch đảo)
    dilated = cv2.dilate(binary_result, kernel, iterations=2)

    # Bước 5: Nghịch đảo lại để được vùng đen giãn nở
    dilated_result = cv2.bitwise_not(dilated)

    # Bước 6: Chuyển ảnh giãn nở thành ảnh nhị phân
    _, binary_final = cv2.threshold(dilated_result, 50, 255, cv2.THRESH_BINARY)

    # Chuyển kết quả từ numpy array trở lại PIL Image
    result_img_pil = Image.fromarray(binary_final)

    # Trả về ảnh kết quả
    return result_img_pil
def draw_dots(image):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    num_dots = random.randint(1, 15)  # Số lượng chấm ngẫu nhiên
    for _ in range(num_dots):
        # Vị trí ngẫu nhiên trên canvas
        x, y = random.randint(0, width), random.randint(0, height)
        # Kích thước ngẫu nhiên cho mỗi chấm
        radius = random.randint(1, 10)
        color = (0, 0, 0)  # Màu đen

        # Vẽ một chấm tròn tại vị trí ngẫu nhiên
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    
    # Trả về hình ảnh đã thay đổi
    return image


# Hàm vẽ đường thẳng (lines) nhận và trả về PIL image
def draw_lines(image):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    num_lines = random.randint(1, 5)  # Số lượng đường ngẫu nhiên
    for _ in range(num_lines):
        # Vị trí điểm đầu và điểm cuối của đường thẳng ngẫu nhiên
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        
        # Độ dày và màu sắc ngẫu nhiên cho đường thẳng
        line_width = random.randint(1, 5)
        line_color = (0, 0, 0)  # Màu đen
        
        # Vẽ đường thẳng
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=line_width)
    
    # Trả về hình ảnh đã thay đổi
    return image



# Hàm vẽ các đường cong uốn éo ngẫu nhiên với độ smooth cao hơn
def bezier_curve(points, t):
    # Sử dụng công thức Bezier cho bậc n (tùy vào số lượng điểm)
    n = len(points) - 1
    x = 0
    y = 0
    for i, (px, py) in enumerate(points):
        binomial_coeff = comb(n, i)  # Hệ số nhị thức
        term = binomial_coeff * ((1 - t) ** (n - i)) * (t ** i)
        x += term * px
        y += term * py
    return (x, y)

# Hàm tính toán hệ số nhị thức
from math import comb

# Hàm vẽ các đường cong Bezier ngẫu nhiên
def draw_smooth_random_curves(image, num_curves=3):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    for _ in range(num_curves):
        # Tạo số lượng điểm ngẫu nhiên cho mỗi đường cong (từ 3 đến 5 điểm)
        num_points = random.randint(1,4)
        points = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_points)]  # Các điểm ngẫu nhiên
        
        # Tăng số lượng điểm để đường mượt hơn
        bezier_points = [bezier_curve(points, t) for t in [i/200.0 for i in range(201)]]  # 201 điểm
        
        # Chọn màu ngẫu nhiên: 50% màu đen, 50% màu khác
        line_color = (0, 0, 0)  # Màu đen

        # Vẽ đường cong Bezier, tăng độ dày width cho mượt hơn
        draw.line(bezier_points, fill=line_color, width=4)
    
    # Trả về hình ảnh sau khi đã vẽ các đường cong
    return image
    