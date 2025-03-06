import pandas as pd
from torch.utils.data import Dataset
from typing import Dict, Any, Tuple


class PhishingDataset(Dataset):
    def __init__(self: "PhishingDataset", csv_file_path: str) -> None:
        self.data: pd.DataFrame = pd.read_csv(csv_file_path)

    def __len__(self: "PhishingDataset") -> int:
        return len(self.data)

    def __getitem__(self: "PhishingDataset", idx: int) -> Tuple[str, int]:
        url = self.data.iloc[idx, 0]
        label = self.data.iloc[idx, 1]
        return url, label

    def get_stats(self: "PhishingDataset") -> Dict[str, Any]:
        labels = self.data["label"].unique()
        stats = [
            {
                "Label": label,
                "Count": len(self.data[self.data["label"] == label]),
                "Percent": round(
                    len(self.data[self.data["label"] == label]) / len(self.data) * 100,
                    2,
                ),
            }
            for label in labels
        ]
        return stats

    def print_stats(self: "PhishingDataset") -> None:
        stats = self.get_stats()
        for stat in stats:
            print(
                f"Label: {stat['Label']}, Count: {stat['Count']}, Percent: {stat['Percent']}%"
            )
