import torch


def create_heatmap(
    x,
    y,
    size=64,
    sigma=2.0
):
    scale = size / 256.0

    cx = x * scale
    cy = y * scale

    yy, xx = torch.meshgrid(
        torch.arange(size, dtype=torch.float32),
        torch.arange(size, dtype=torch.float32),
        indexing="ij"
    )

    heatmap = torch.exp(
        -(
            (xx - cx) ** 2 +
            (yy - cy) ** 2
        ) / (2 * sigma ** 2)
    )

    heatmap = heatmap / heatmap.max()

    return heatmap.unsqueeze(0)


def heatmap_to_point(heatmap):
    heatmap = heatmap.squeeze()

    index = torch.argmax(heatmap)

    h, w = heatmap.shape

    y = index // w
    x = index % w

    x = x.float() * 256.0 / w
    y = y.float() * 256.0 / h

    return torch.tensor([x, y])