import numpy as np
from dinov2_heatmap_dataset import DinoV2HeatmapDataset

dataset = DinoV2HeatmapDataset(augment=False)

dx = []
dy = []

for i in range(len(dataset)):
    d = dataset[i]["displacement"]
    dx.append(float(d[0]))
    dy.append(float(d[1]))

dx = np.array(dx)
dy = np.array(dy)

print("\nOVERLAY TARGET DISTRIBUTION")
print("=" * 50)

print(f"Samples : {len(dataset)}")

print(f"\nDX")
print(f"Min    : {dx.min():.3f} px")
print(f"Max    : {dx.max():.3f} px")
print(f"Mean   : {dx.mean():.3f} px")
print(f"Std    : {dx.std():.3f} px")

print(f"\nDY")
print(f"Min    : {dy.min():.3f} px")
print(f"Max    : {dy.max():.3f} px")
print(f"Mean   : {dy.mean():.3f} px")
print(f"Std    : {dy.std():.3f} px")

print("\nTARGET POINT")
print(f"X range: {128 + dx.min():.3f} → {128 + dx.max():.3f}")
print(f"Y range: {128 + dy.min():.3f} → {128 + dy.max():.3f}")