import torch
from overlay_model import OverlayModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = OverlayModel().to(device)

x = torch.randn(2, 1, 256, 256).to(device)

with torch.no_grad():
    y = model(x)

print("Device:", device)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

print("Input:", x.shape)
print("Output:", y.shape)
print("Prediction:", y)