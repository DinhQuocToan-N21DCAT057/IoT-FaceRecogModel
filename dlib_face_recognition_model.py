import cv2
import dlib
import numpy as np
import requests

# Đường dẫn tới các mô hình Dlib
shape_predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_recognition_model_path = 'dlib_face_recognition_resnet_model_v1.dat'

# Tạo bộ phát hiện và nhận diện khuôn mặt
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(shape_predictor_path)
face_recognizer = dlib.face_recognition_model_v1(face_recognition_model_path)

# Tải vector đặc trưng của owner
owner_face_vector = np.load('owner_face_vectors.npy')

# # Sử dụng IP WebCam
# ip_camera_url = 'http://10.252.2.114:8080/video'  # Thay bằng địa chỉ IP của bạn
# cap = cv2.VideoCapture(ip_camera_url)

cap = cv2.VideoCapture(0)

def euclidean_distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không đọc được khung hình từ camera.")
        break

    faces = detector(frame)

    for face in faces:
        shape = shape_predictor(frame, face)
        face_descriptor = face_recognizer.compute_face_descriptor(frame, shape)

        # So sánh khoảng cách giữa khuôn mặt nhận diện và owner
        distance = euclidean_distance(face_descriptor, owner_face_vector)

        if distance < 0.6:  # Nếu khoảng cách nhỏ hơn ngưỡng (chỉ số nhận diện chính xác)
            cv2.putText(frame, 'Owner', (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Gọi HTTP Request để bật đèn qua Blynk
            url = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v1=1'
            requests.get(url)
            print("Predict: Is Owner, Distance: ", distance)

        else:
            cv2.putText(frame, 'Unknown', (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            print("Predict: Not Owner, Distance: ", distance)

        # Vẽ hình chữ nhật xung quanh khuôn mặt
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (255, 0, 0), 2)

    cv2.imshow('Face Recognition', frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
