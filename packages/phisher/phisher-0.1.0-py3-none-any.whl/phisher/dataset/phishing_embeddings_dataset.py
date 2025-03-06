import torch
from torch.utils.data import Dataset
from typing import List, Tuple, Dict, Any
import pandas as pd


class PhishingEmbeddingDataset(Dataset):
    def __init__(
        self: "PhishingEmbeddingDataset", csv_file_path: str, max_length: int = 200
    ) -> None:
        self.data: pd.DataFrame = pd.read_csv(csv_file_path)
        self.max_length: int = max_length
        self.alphabet: List[str] = list(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'()*+,;"
        ) + [" "]
        self.char_to_idx: Dict[str, int] = {
            char: idx for idx, char in enumerate(self.alphabet, start=1)
        }  # Start indexing from 1
        self.pad_idx = 0  # Padding index for unused positions

    def parse_url(self: "PhishingEmbeddingDataset", url: str) -> str:
        parsed_url = url.split("://")[-1]
        if "/" in parsed_url:
            parsed_url = parsed_url.split("/")[0]
        return parsed_url

    def pad_or_trim(self: "PhishingEmbeddingDataset", url: str) -> List[int]:
        url_indices = [self.char_to_idx.get(char, self.pad_idx) for char in url]
        if len(url_indices) > self.max_length:
            url_indices = url_indices[: self.max_length]
        else:
            url_indices.extend([self.pad_idx] * (self.max_length - len(url_indices)))
        return url_indices

    def __len__(self: "PhishingEmbeddingDataset") -> int:
        return len(self.data)

    def __getitem__(
        self: "PhishingEmbeddingDataset", idx: int
    ) -> Tuple[torch.Tensor, int]:
        url = self.data.iloc[idx, 0]
        label = self.data.iloc[idx, 1]

        parse_url = self.parse_url(url)
        encoded_url = self.pad_or_trim(parse_url)

        return torch.tensor(encoded_url, dtype=torch.long), label

    def get_stats(self: "PhishingEmbeddingDataset") -> Dict[str, Any]:
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

    def print_stats(self: "PhishingEmbeddingDataset") -> None:
        stats = self.get_stats()
        for stat in stats:
            print(
                f"Label: {stat['Label']}, Count: {stat['Count']}, Percent: {stat['Percent']}%"
            )
