import torch
import torch.nn as nn
import torch.nn.functional as F

from .phisher_model import PhisherModel


class PhisherEmbeddingModel(PhisherModel, nn.Module):
    def __init__(
        self: "PhisherEmbeddingModel",
        vocab_size: int,
        embedding_dim: int,
        out_features: int = 1,
    ) -> None:
        PhisherModel.__init__(self, out_features=out_features)
        nn.Module.__init__(self)

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size, embedding_dim=embedding_dim, padding_idx=0
        )
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=6, kernel_size=(5, 1))
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=(5, 1))
        self.fc1 = nn.Linear(in_features=12 * 47 * 100, out_features=120)
        self.fc2 = nn.Linear(in_features=120, out_features=60)
        self.out = nn.Linear(in_features=60, out_features=out_features)

    def forward(self: "PhisherEmbeddingModel", x: torch.Tensor) -> torch.Tensor:
        x = self.embedding(x)
        x = x.unsqueeze(1)

        x = self.conv1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=(2, 1), stride=(2, 1))

        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=(2, 1), stride=(2, 1))

        x = x.reshape(-1, 12 * 47 * 100)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.out(x)
        return x
