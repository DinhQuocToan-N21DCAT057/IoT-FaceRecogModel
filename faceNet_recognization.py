import cv2
import torch
import numpy as np
from PIL import Image
from sympy.printing.codeprinter import requires
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1, MTCNN
import requests
from io import BytesIO

# Thiết lập device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load mô hình phát hiện khuôn mặt (MTCNN) và mô hình Facenet
mtcnn = MTCNN(keep_all=True, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Load vector đặc trưng của owner
owner_face_vectors = np.load('owner_face_vectors_esp32-cam.npy')

# Cấu hình URL của ESP32-CAM
ESP32_CAM_IP = "10.252.13.0"  # Thay đổi IP theo ESP32-CAM của bạn
stream_url = f"http://{ESP32_CAM_IP}/stream"  # URL stream
capture_url = f"http://{ESP32_CAM_IP}/capture"  # URL để lấy ảnh đơn lẻ

# ThingSpeak configuration
THINGSPEAK_API_KEY = "131WMWJP4Y2VLLMO"  # API Key của kênh
THINGSPEAK_CHANNEL_ID = 2754157  # Channel Number
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# Blynk API URL
BLYNK_URL_ON_V1 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v1=1'
BLYNK_URL_OFF_V1 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v1=0'
BLYNK_URL_ON_V2 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v2=1'
BLYNK_URL_OFF_V2 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v2=0'
BLYNK_URL_ON_V3 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v3=1'
BLYNK_URL_OFF_V3 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v3=0'
BLYNK_URL_ON_V4 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v4=1'
BLYNK_URL_OFF_V4 = 'https://sgp1.blynk.cloud/external/api/update?token=cGxwzESkTcImx2FoPB_j29NGW-TW9PtT&v4=0'

# Biến đổi cho ảnh đầu vào
transform = transforms.Compose([transforms.Resize((160, 160)), transforms.ToTensor()])


def extract_face_vector(face_image):
    face_image = transform(face_image).unsqueeze(0).to(device)
    with torch.no_grad():
        face_embedding = model(face_image)
    return face_embedding.cpu().numpy()


def euclidean_distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))


def get_frame_from_esp32():
    try:
        # Phương pháp 1: Lấy frame từ MJPEG stream
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                return frame

        # Phương pháp 2: Lấy ảnh đơn lẻ qua HTTP request
        response = requests.get(capture_url)
        if response.status_code == 200:
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return frame

    except Exception as e:
        print(f"Lỗi khi lấy frame: {e}")
    return None


# Gủi API tới Blynk Cloud Server
def send_blynk_request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Blynk request sent: {url}")
        else:
            print(f"Blynk request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending Blynk request: {e}")


# Gửi dữ liệu nhận diện lên ThingSpeak
def send_to_thingspeak(owner_detected, min_distance):
    try:
        # Xác định trạng thái nhận diện (1 = Owner, 0 = Unknown)
        data = {
            "api_key": THINGSPEAK_API_KEY,
            "field1": int(owner_detected),  # Trạng thái nhận diện
            "field2": round(min_distance, 2)  # Khoảng cách Euclidean
        }
        response = requests.post(THINGSPEAK_URL, params=data)
        if response.status_code == 200:
            print(f"Data sent to ThingSpeak: {data}")
        else:
            print(f"Failed to send data. HTTP status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to ThingSpeak: {e}")


# Thử kết nối với MJPEG stream
cap = cv2.VideoCapture(capture_url)

# Trạng thái ban đầu
owner_detected_count = 0  # Số lần phát hiện owner
required_owner_count = 5  # Số lần phát hiện liên tiếp để xác nhận owner
is_owner_confirmed = False

while True:
    frame = get_frame_from_esp32()
    if frame is None:
        print("Không lấy được frame từ ESP32-CAM")
        continue

    # Phát hiện khuôn mặt bằng MTCNN
    boxes, _ = mtcnn.detect(frame)
    current_state = "Unknown"

    if boxes is not None:
        for box in boxes:
            # Cắt phần khuôn mặt ra từ khung hình
            x1, y1, x2, y2 = [int(b) for b in box]
            face = frame[y1:y2, x1:x2]
            face_pil = Image.fromarray(face)  # Chuyển sang dạng PIL Image

            # Trích xuất vector đặc trưng của khuôn mặt
            face_vector = extract_face_vector(face_pil)

            # So sánh với vector của owner
            min_distance = float('inf')
            for owner_face_vector in owner_face_vectors:
                distance = euclidean_distance(face_vector, owner_face_vector)
                min_distance = min(min_distance, distance)

            # Nếu khoảng cách nhỏ hơn ngưỡng, nhận diện là owner
            if min_distance < 0.6:
                owner_detected_count += 1
                print(f"Owner detected! Count: {owner_detected_count}, Distance: {min_distance}")
                send_to_thingspeak(1, min_distance)  # Gửi trạng thái lên ThingSpeak
                cv2.putText(frame, 'Owner', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                owner_detected_count = 0  # Reset đếm nếu không phải owner
                send_to_thingspeak(0, min_distance)
                print(f"Unknown detected, Distance: {min_distance}")
                cv2.putText(frame, 'Unknown', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Vẽ hình chữ nhật quanh khuôn mặt
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # Xác nhận owner và bật đèn
            if owner_detected_count >= required_owner_count:
                print("Owner confirmed! Turning on the light.")
                send_blynk_request(BLYNK_URL_ON_V1)
                send_blynk_request(BLYNK_URL_ON_V2)
                send_blynk_request(BLYNK_URL_ON_V3)
                send_blynk_request(BLYNK_URL_ON_V4)
                is_owner_confirmed = True
                break

    # Nếu không phát hiện owner, tắt đèn
    if owner_detected_count == 0:
        send_blynk_request(BLYNK_URL_OFF_V1)
        send_blynk_request(BLYNK_URL_OFF_V2)
        send_blynk_request(BLYNK_URL_OFF_V3)
        send_blynk_request(BLYNK_URL_OFF_V4)

    # Hiển thị khung hình
    cv2.imshow('Face Recognition', frame)

    # Thoát khi nhấn phím 'q' hoặc đã xác nhận owner
    if cv2.waitKey(1) & 0xFF == ord('q') or is_owner_confirmed:
        break

cap.release()
cv2.destroyAllWindows()
print("Program terminated.")
