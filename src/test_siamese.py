import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from siamese_dataset import SiameseLocalizationDataset
from siamese_model import SiameseCNN


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

dataset = SiameseLocalizationDataset(
    start=0,
    end=5000,
    training=False
)

sample = dataset[0]

reference = sample["reference"].unsqueeze(0).to(device)
search = sample["search"].unsqueeze(0).to(device)

model = SiameseCNN().to(device)

with torch.no_grad():
    prediction = model(reference, search)

print("Device:", device)
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
print("Reference:", reference.shape)
print("Search:", search.shape)
print("Prediction:", prediction)
print("Target:", sample["target"])

error = torch.abs(prediction[0] - sample["target"].to(device))

pixel_error = error * 256

print("Pixel error X:", pixel_error[0].item())
print("Pixel error Y:", pixel_error[1].item())