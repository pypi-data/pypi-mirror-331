import torch
import torch.nn as nn
import torch.nn.functional as F

from .phisher_model import PhisherModel


class PhisherOneHotModel(PhisherModel, nn.Module):
    def __init__(self: "PhisherOneHotModel", out_features: int = 1) -> None:
        PhisherModel.__init__(self, out_features=out_features)
        nn.Module.__init__(self)

        self.conv1 = nn.Conv2d(in_channels=1, out_channels=6, kernel_size=(5, 5))
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=(5, 5))

        self.fc1 = nn.Linear(in_features=12 * 47 * 18, out_features=120)
        self.fc2 = nn.Linear(in_features=120, out_features=60)
        self.out = nn.Linear(in_features=60, out_features=out_features)

    def forward(self: "PhisherOneHotModel", x: torch.Tensor) -> torch.Tensor:
        x = x.unsqueeze(1)
        x = self.conv1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)

        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)

        # Flatten
        x = x.reshape(-1, 12 * 47 * 18)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.out(x)
        return x
