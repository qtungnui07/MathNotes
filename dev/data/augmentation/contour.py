import cv2
import numpy as np
from PIL import Image

def find_and_merge_contours(image):
    img_array = np.array(image)
    
    # Kiểm tra nếu ảnh đã là grayscale
    if len(img_array.shape) == 2:  # Ảnh grayscale có 2 chiều
        gray_image = img_array
    else:
        gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    _, thresh = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    x_min, y_min, x_max, y_max = np.inf, np.inf, -np.inf, -np.inf
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)

    if x_min == np.inf:
        return image, (0, 0, image.size[0], image.size[1])
    
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    return cropped_image, (x_min, y_min, x_max, y_max)