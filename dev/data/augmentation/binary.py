import cv2
import numpy as np
from PIL import Image

def binary_image(image, threshold_value=90):
    """
    Chuyển ảnh PIL thành ảnh nhị phân.

    Args:
        image (PIL.Image): Đối tượng ảnh PIL cần nhị phân hóa.
        threshold_value (int): Giá trị ngưỡng để phân chia trắng và đen. Mặc định là 127.

    Returns:
        PIL.Image: Ảnh nhị phân dưới dạng PIL.Image.
    """
    # Chuyển ảnh PIL sang ảnh xám (grayscale)
    gray_img = image.convert('L')  # 'L' là mode cho ảnh xám (grayscale)

    # Chuyển ảnh xám thành mảng numpy
    np_img = np.array(gray_img)

    # Áp dụng ngưỡng để nhị phân hóa
    binary_np_img = np.where(np_img >= threshold_value, 255, 0).astype(np.uint8)

    # Chuyển mảng numpy thành ảnh PIL
    binary_pil_img = Image.fromarray(binary_np_img)

    return binary_pil_img