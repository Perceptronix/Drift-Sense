import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.block(x)


class FPN(nn.Module):
    def __init__(self, in_ch, out_ch=256):
        super().__init__()
        self.lateral = nn.Conv2d(in_ch, out_ch, 1)
        self.conv = ConvBlock(out_ch, out_ch)

    def forward(self, x):
        x = self.lateral(x)
        return self.conv(x)


class HeatmapHead(nn.Module):
    def __init__(self, in_ch=256):
        super().__init__()
        self.head = nn.Sequential(
            nn.Conv2d(in_ch, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 1, 1)
        )

    def forward(self, x):
        return torch.sigmoid(self.head(x))


class DINOv2FPNHeatmap(nn.Module):
    def __init__(self):
        super().__init__()

        self.backbone = torch.hub.load(
            "facebookresearch/dinov2",
            "dinov2_vits14"
        )

        self.backbone_dim = 384

        self.fpn = FPN(self.backbone_dim, 256)

        self.head = HeatmapHead(256)

    def forward(self, x):
        if x.shape[1] == 1:
            x = x.repeat(1, 3, 1, 1)

        x = F.interpolate(
            x,
            size=(518, 518),
            mode="bilinear",
            align_corners=False
        )

        features = self.backbone.forward_features(x)

        tokens = features["x_norm_patchtokens"]

        b, n, c = tokens.shape

        h = w = int(n ** 0.5)

        features = tokens.transpose(1, 2).reshape(
            b, c, h, w
        )

        features = self.fpn(features)

        heatmap = self.head(features)

        heatmap = F.interpolate(
            heatmap,
            size=(64, 64),
            mode="bilinear",
            align_corners=False
        )

        return heatmap


def heatmap_to_point(heatmap):
    b, _, h, w = heatmap.shape

    flat = heatmap.view(b, -1)

    idx = flat.argmax(dim=1)

    y = idx // w
    x = idx % w

    x = x.float() * 4
    y = y.float() * 4

    return torch.stack([x, y], dim=1)


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Device:", device)

    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    model = DINOv2FPNHeatmap().to(device)

    x = torch.randn(1, 1, 256, 256).to(device)

    with torch.no_grad():
        heatmap = model(x)
        point = heatmap_to_point(heatmap)

    print("Input:", x.shape)
    print("Heatmap:", heatmap.shape)
    print("Point:", point)