import cv2
import requests

# Đường dẫn đến mô hình đã huấn luyện
model_path = 'owner_face_model.yml'
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read(model_path)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Sử dụng webcam
cap = cv2.VideoCapture(0)

# Sử dụng IP WebCam
# ip_camera_url = 'http://192.168.1.3:8080/video'  # Địa chỉ IP của camera ở nhà
# ip_camera_url = 'http://10.252.6.168:8080/video'  # Địa chỉ IP của camera ở trường
# cap = cv2.VideoCapture(ip_camera_url)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y + h, x:x + w]
        label, confidence = face_recognizer.predict(face)

        if label == 1 and confidence < 50:  # Nếu nhận diện đúng owner
            cv2.putText(frame, 'Owner', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Gọi HTTP Request để bật đèn
            url = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v1=1'
            requests.get(url)
            print("Predict: Is Owner, Confidence: ", confidence)

        else:
            cv2.putText(frame, 'Unknown', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            print("Predict: Not Owner, Confidence: ", confidence)

        # Hiển thị khung hình
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('Face Recognition', frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
