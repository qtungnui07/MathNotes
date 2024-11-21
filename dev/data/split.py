import os
import shutil
import random

# Đường dẫn gốc và thư mục đích
source_folder = 'datasets'
train_folder = 'datasets_train'
test_folder = 'datasets_test'

# Tạo thư mục train và test nếu chưa có
os.makedirs(train_folder, exist_ok=True)
os.makedirs(test_folder, exist_ok=True)

# Tỉ lệ chia
split_ratio = 0.8

# Hàm chia file với tỷ lệ giữ cấu trúc thư mục
def split_data(source, train_dest, test_dest, ratio=0.8):
    for root, dirs, files in os.walk(source):
        # Xác định đường dẫn đích của train và test với cấu trúc folder gốc
        relative_path = os.path.relpath(root, source)
        train_path = os.path.join(train_dest, relative_path)
        test_path = os.path.join(test_dest, relative_path)
        
        # Tạo folder đích nếu chưa có
        os.makedirs(train_path, exist_ok=True)
        os.makedirs(test_path, exist_ok=True)
        
        # Lọc các file để random chia tỉ lệ
        files = [f for f in files if os.path.isfile(os.path.join(root, f))]
        random.shuffle(files)  # Trộn files để random chia
        
        # Chia file theo tỉ lệ
        train_count = int(len(files) * ratio)
        train_files = files[:train_count]
        test_files = files[train_count:]
        
        # Chuyển file vào train folder
        for f in train_files:
            shutil.copy2(os.path.join(root, f), os.path.join(train_path, f))
        
        # Chuyển file vào test folder
        for f in test_files:
            shutil.copy2(os.path.join(root, f), os.path.join(test_path, f))

# Chạy hàm chia file
split_data(source_folder, train_folder, test_folder, split_ratio)
