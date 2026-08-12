from dinov2_heatmap_dataset import DINOv2HeatmapDataset
import numpy as np

dataset = DINOv2HeatmapDataset()

xs = []
ys = []

for i in range(min(len(dataset), 5000)):
    sample = dataset[i]
    point = sample["point"]

    xs.append(float(point[0]))
    ys.append(float(point[1]))

print("\nTARGET DISTRIBUTION")
print("=" * 50)

print(f"Samples checked : {len(xs)}")
print(f"X min          : {min(xs):.2f}")
print(f"X max          : {max(xs):.2f}")
print(f"X mean         : {np.mean(xs):.2f}")
print(f"X std          : {np.std(xs):.2f}")

print(f"Y min          : {min(ys):.2f}")
print(f"Y max          : {max(ys):.2f}")
print(f"Y mean         : {np.mean(ys):.2f}")
print(f"Y std          : {np.std(ys):.2f}")

print("\nFIRST 20 TARGETS")
for i in range(min(20, len(xs))):
    print(f"{i:4d}: X={xs[i]:7.2f}, Y={ys[i]:7.2f}")