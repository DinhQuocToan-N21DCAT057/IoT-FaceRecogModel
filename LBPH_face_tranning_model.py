import cv2
import numpy as np
import os

# Đường dẫn đến thư mục chứa ảnh
face_dir = 'faces/owner'

# Tạo bộ nhận diện khuôn mặt
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Hàm lấy dữ liệu huấn luyện
def get_training_data(directory):
    faces = []
    labels = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            img_path = os.path.join(directory, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            faces.append(img)
            labels.append(1)  # Nhãn '1' đại diện cho owner

    return faces, labels

# Lấy dữ liệu huấn luyện
faces, labels = get_training_data(face_dir)

# Huấn luyện mô hình nhận diện
face_recognizer.train(faces, np.array(labels))

# Lưu mô hình để sử dụng sau
face_recognizer.save('owner_face_model.yml')
