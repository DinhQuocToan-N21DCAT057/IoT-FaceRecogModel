import cv2
import torch
import numpy as np
from PIL import Image
import os
from datetime import datetime
from facenet_pytorch import MTCNN
import requests
import time

# Thiết lập device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Khởi tạo MTCNN để phát hiện khuôn mặt
mtcnn = MTCNN(keep_all=True, device=device)

# Tạo thư mục để lưu ảnh khuôn mặt
SAVE_DIR = 'face_captures'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def get_frame_from_esp32(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return frame
    except Exception as e:
        print(f"Lỗi khi lấy frame: {e}")
    return None


def save_face(face_img, index):
    # Kiểm tra ảnh có hợp lệ không
    if face_img is None or face_img.size == 0:
        print("Ảnh không hợp lệ để lưu")
        return None

    # Kiểm tra kích thước ảnh
    if face_img.shape[0] < 10 or face_img.shape[1] < 10:
        print("Kích thước ảnh quá nhỏ")
        return None

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SAVE_DIR, f'face_{index}_{timestamp}.jpg')
        success = cv2.imwrite(filename, face_img)

        if success:
            return filename
        else:
            print("Không thể lưu ảnh")
            return None
    except Exception as e:
        print(f"Lỗi khi lưu ảnh: {e}")
        return None


def main():
    # Cấu hình URL của ESP32-CAM
    ESP32_CAM_IP = "10.251.3.232"  # Thay đổi IP theo ESP32-CAM của bạn
    capture_url = f"http://{ESP32_CAM_IP}/capture"  # URL để lấy ảnh đơn lẻ

    face_count = 0
    total_faces_needed = 20  # Số lượng ảnh khuôn mặt cần thu thập

    print("Bắt đầu thu thập ảnh khuôn mặt...")
    print("Nhấn 'c' để chụp ảnh")
    print("Nhấn 'q' để thoát")

    while face_count < total_faces_needed:
        frame = get_frame_from_esp32(capture_url)

        if frame is None:
            print("Không lấy được frame từ camera")
            time.sleep(1)  # Đợi 1 giây trước khi thử lại
            continue

        # Phát hiện khuôn mặt
        try:
            boxes, _ = mtcnn.detect(frame)
        except Exception as e:
            print(f"Lỗi khi phát hiện khuôn mặt: {e}")
            continue

        # Vẽ khung và thông tin
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                x1, y1, x2, y2 = [int(b) for b in box]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Hiển thị số ảnh đã chụp
        cv2.putText(frame, f'Captured: {face_count}/{total_faces_needed}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Face Capture', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            if boxes is not None and len(boxes) > 0:
                # Lấy khuôn mặt lớn nhất trong frame
                areas = [(box[2] - box[0]) * (box[3] - box[1]) for box in boxes]
                largest_face_idx = areas.index(max(areas))
                box = boxes[largest_face_idx]
                x1, y1, x2, y2 = [int(b) for b in box]

                # Thêm padding cho khuôn mặt
                padding = 30
                h, w = frame.shape[:2]
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)

                # Cắt và kiểm tra khuôn mặt
                face_img = frame[y1:y2, x1:x2]

                if face_img is not None and face_img.size > 0:
                    filename = save_face(face_img, face_count)
                    if filename:
                        print(f"Đã lưu ảnh: {filename}")
                        face_count += 1
                        time.sleep(0.5)  # Đợi 0.5 giây giữa các lần chụp
                    else:
                        print("Không thể lưu ảnh khuôn mặt")
                else:
                    print("Không thể cắt ảnh khuôn mặt")
            else:
                print("Không phát hiện được khuôn mặt!")

    cv2.destroyAllWindows()
    print(f"\nĐã thu thập xong {face_count} ảnh khuôn mặt!")
    print(f"Ảnh được lưu trong thư mục: {SAVE_DIR}")


if __name__ == "__main__":
    main()