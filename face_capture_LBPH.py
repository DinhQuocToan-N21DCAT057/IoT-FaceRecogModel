import cv2
import os
import time  # Thêm thư viện này để tạo thời gian trễ

# Tạo thư mục để lưu ảnh nếu chưa có
face_dir = 'faces/owner'
if not os.path.exists(face_dir):
    os.makedirs(face_dir)

# Sử dụng Haar Cascade để phát hiện khuôn mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Khởi động webcam
cap = cv2.VideoCapture(0)
count = 180  # Đếm số lượng ảnh thu thập

while True:
    ret, frame = cap.read()  # Đọc frame từ webcam
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Chuyển sang ảnh xám
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        # Lưu ảnh đã cắt chứa khuôn mặt
        face = gray[y:y+h, x:x+w]
        cv2.imwrite(f"{face_dir}/face_{count}.jpg", face)

        # Hiển thị khung hình với khuôn mặt được phát hiện
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imshow('Collecting Faces', frame)

        # Thêm thời gian trễ giữa các lần chụp (1 giây)
        time.sleep(1)  # Delay 1 giây giữa các lần chụp ảnh

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # Dừng thu thập khi đạt 100 ảnh
    elif count >= 240:
        break

cap.release()
cv2.destroyAllWindows()
