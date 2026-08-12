from dinov2_heatmap_dataset import DinoV2HeatmapDataset

dataset = DinoV2HeatmapDataset(augment=False)

print("\nTARGET CHECK\n")

for i in range(min(20, len(dataset))):
    s = dataset[i]

    print(
        f"{i:02d} | "
        f"{s['sample']} | "
        f"DX={s['displacement'][0]:+8.3f} px | "
        f"DY={s['displacement'][1]:+8.3f} px | "
        f"Point=({s['point'][0]:.3f}, {s['point'][1]:.3f})"
    )