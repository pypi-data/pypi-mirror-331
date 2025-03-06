import torch
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl


class PhishingDataModule(pl.LightningDataModule):
    def __init__(
        self: "PhishingDataModule", dataset: Dataset, batch_size: int = 32
    ) -> None:
        super().__init__()
        self.dataset = dataset
        self.batch_size = batch_size

    def split_data(
        self: "PhishingDataModule", train_size: float, val_size: float
    ) -> None:
        total_size = len(self.dataset)
        train_size = int(train_size * total_size)
        val_size = int(val_size * total_size)
        test_size = total_size - train_size - val_size
        self.train_dataset, self.val_dataset, self.test_dataset = (
            torch.utils.data.random_split(
                self.dataset, [train_size, val_size, test_size]
            )
        )

    def setup(
        self: "PhishingDataModule",
        train_size: float = 0.7,
        val_size: float = 0.1,
        stage=None,
    ) -> None:
        self.split_data(train_size, val_size)

    def train_dataloader(self: "PhishingDataModule") -> DataLoader:
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=7,
            persistent_workers=True,
        )

    def val_dataloader(self: "PhishingDataModule") -> DataLoader:
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            num_workers=7,
            persistent_workers=True,
        )

    def test_dataloader(self: "PhishingDataModule") -> DataLoader:
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            num_workers=7,
            persistent_workers=True,
        )
