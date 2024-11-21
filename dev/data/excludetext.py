import os
import random
from PIL import Image, ImageDraw
from augmentation.create_background import create_random_canvas
from augmentation.dilate import dilateimg

def remove_white_background(img):
    # Ensure the image is in RGBA (with alpha channel)
    img = img.convert("RGBA")
    
    # Get pixel data
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Check if the pixel is white (255, 255, 255)
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            # Replace white with transparency (0 alpha)
            new_data.append((255, 255, 255, 0))  # (R, G, B, A)
        else:
            # Keep the other pixels unchanged
            new_data.append(item)
    
    # Update pixel data
    img.putdata(new_data)
    
    return img

def place_random_image_in_canvas(scale_min=0.1, scale_max=0.5):
    # Get a random image from the folder
    folder_path = 'math_1'
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    random_image_file = random.choice(image_files)

    # Open the random image
    image_path = os.path.join(folder_path, random_image_file)
    img = Image.open(image_path)
    
    # 25% chance to dilate the image
    if random.random() < 0.25:  # 25% chance
        img = dilateimg(img)

    # Remove the white background
    img = remove_white_background(img)

    # Select a random scale for the image within the given range
    width, height = img.size
    scale_factor = random.uniform(scale_min, scale_max)
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Ensure the image fits within the canvas
    canvas = create_random_canvas()
    canvas_width, canvas_height = canvas.size

    # Adjust the scale factor to make sure the image fits the canvas
    if new_width > canvas_width or new_height > canvas_height:
        scale_factor = min(canvas_width / width, canvas_height / height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

    # Resize the image
    img = img.resize((new_width, new_height))

    # Calculate a random position to paste the image onto the canvas
    max_x = canvas_width - new_width
    max_y = canvas_height - new_height

    # Ensure max_x and max_y are not negative
    if max_x < 0:
        max_x = 0
    if max_y < 0:
        max_y = 0

    # Get a random position within the allowed range
    x_position = random.randint(0, max_x)
    y_position = random.randint(0, max_y)

    # Paste the image onto the canvas at the random position
    canvas.paste(img, (x_position, y_position), img)  # Use alpha channel as a mask

    # Draw the bounding box around the pasted image
    draw = ImageDraw.Draw(canvas)
    bounding_box = [x_position, y_position, x_position + new_width, y_position + new_height]
    draw.rectangle(bounding_box, outline="red", width=5)  # Red bounding box with a width of 5

    # Save the final image with the bounding box to a file
    output_file = 'output_random_image_with_bounding_box.jpg'
    canvas.save(output_file, 'JPEG')
    print(f"Image saved to {output_file}")

# Call the function to execute the process
place_random_image_in_canvas(scale_min=0.5, scale_max=3)
