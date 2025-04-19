import cv2
import dlib
import os
import numpy as np

# Đường dẫn tới các mô hình Dlib
shape_predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_recognition_model_path = 'dlib_face_recognition_resnet_model_v1.dat'

# Tạo bộ phát hiện và nhận diện khuôn mặt
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(shape_predictor_path)
face_recognizer = dlib.face_recognition_model_v1(face_recognition_model_path)

# Đường dẫn tới thư mục chứa các ảnh của owner
owner_folder = 'faces_captured'

# Mảng để chứa vector đặc trưng của tất cả khuôn mặt owner
owner_face_descriptors = []

# Duyệt qua từng file ảnh trong thư mục
for filename in os.listdir(owner_folder):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # Đọc ảnh
        image_path = os.path.join(owner_folder, filename)
        img = cv2.imread(image_path)

        # Phát hiện khuôn mặt
        faces = detector(img)

        if len(faces) == 0:
            print(f"Không tìm thấy khuôn mặt trong ảnh {filename}.")
            continue

        # Xử lý khuôn mặt đầu tiên tìm thấy
        face = faces[0]
        shape = shape_predictor(img, face)
        face_descriptor = face_recognizer.compute_face_descriptor(img, shape)

        # Thêm vector đặc trưng vào danh sách
        owner_face_descriptors.append(np.array(face_descriptor))
        print(f"Trích xuất vector đặc trưng từ {filename} thành công.")

# Lưu toàn bộ vector đặc trưng vào file .npy
np.save('owner_face_vectors.npy', np.array(owner_face_descriptors))
print("Lưu vector đặc trưng khuôn mặt của owner thành công.")
