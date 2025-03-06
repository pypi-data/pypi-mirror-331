import torch
from abc import ABC, abstractmethod


class PhisherModel(ABC):
    def __init__(self: "PhisherModel", out_features: int) -> None:
        super().__init__()
        self.out_features = out_features

    @abstractmethod
    def forward(self: "PhisherModel", x: torch.Tensor) -> torch.Tensor:
        pass
