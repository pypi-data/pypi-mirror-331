import pandas as pd
import torch
from torch.utils.data import Dataset
from typing import Dict, Any, Tuple, List


class PhishingOneHotDataset(Dataset):
    def __init__(
        self: "PhishingOneHotDataset", csv_file_path: str, max_length: int = 200
    ) -> None:
        self.data: pd.DataFrame = pd.read_csv(csv_file_path)
        self.max_length: int = max_length
        self.alphabet: List[str] = list(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'()*+,;"
        ) + [" "]
        self.char_to_idx: Dict[str, int] = {
            char: idx for idx, char in enumerate(self.alphabet)
        }

    def parse_url(self: "PhishingOneHotDataset", url: str) -> str:
        parsed_url = url.split("://")[-1]
        if "/" in parsed_url:
            parsed_url = parsed_url.split("/")[0]
        return parsed_url

    def pad_or_trim(self: "PhishingOneHotDataset", url: str) -> str:
        if len(url) > self.max_length:
            url = url[: self.max_length]
        else:
            url = url = url.ljust(self.max_length, " ")
        return url

    def encode_url(self: "PhishingOneHotDataset", url: str) -> torch.Tensor:
        url = self.pad_or_trim(url)
        matrix = torch.zeros(self.max_length, len(self.alphabet))
        for i, char in enumerate(url):
            if char in self.char_to_idx:
                matrix[i, self.char_to_idx[char]] = 1
        return matrix

    def __len__(self: "PhishingOneHotDataset") -> int:
        return len(self.data)

    def __getitem__(
        self: "PhishingOneHotDataset", idx: int
    ) -> Tuple[torch.Tensor, int]:
        url = self.data.iloc[idx, 0]
        label = self.data.iloc[idx, 1]

        parse_url = self.parse_url(url)
        url = self.encode_url(url)

        return url, label

    def get_stats(self: "PhishingOneHotDataset") -> Dict[str, Any]:
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

    def print_stats(self: "PhishingOneHotDataset") -> None:
        stats = self.get_stats()
        for stat in stats:
            print(
                f"Label: {stat['Label']}, Count: {stat['Count']}, Percent: {stat['Percent']}%"
            )
