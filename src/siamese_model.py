import torch
import torch.nn as nn


class Encoder(nn.Module):
    def __init__(self):
        super().__init__()

        self.net = nn.Sequential(
            nn.Conv2d(1, 32, 5, 2, 2),
            nn.BatchNorm2d(32),
            nn.ReLU(),

            nn.Conv2d(32, 64, 3, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),

            nn.Conv2d(64, 128, 3, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(),

            nn.Conv2d(128, 256, 3, 2, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(),

            nn.AdaptiveAvgPool2d(1)
        )

    def forward(self, x):
        return self.net(x).flatten(1)


class SiameseCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = Encoder()

        self.head = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(256, 64),
            nn.ReLU(),

            nn.Linear(64, 2),
            nn.Sigmoid()
        )

    def forward(self, reference, search):
        ref_features = self.encoder(reference)
        search_features = self.encoder(search)

        features = torch.cat(
            [ref_features, search_features],
            dim=1
        )

        return self.head(features)