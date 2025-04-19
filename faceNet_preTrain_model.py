from facenet_pytorch import InceptionResnetV1
import torch

# Tải mô hình FaceNet đã được huấn luyện trên dataset VGGFace2
model = InceptionResnetV1(pretrained='vggface2').eval()

# Kiểm tra xem có GPU không, nếu có thì sử dụng
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
