import zipfile
import os
import gdown
import pandas as pd
from typing import List, Dict


def unzip_file(file_path: str) -> str:
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall()
        return zip_ref.namelist()[0]


def clean_up(file_paths: List[str]) -> None:
    for file_path in file_paths:
        os.remove(file_path)


def prepare_phish_dataset(
    target_file_path: str,
    gdown_link: str,
    columns: List[str] = ["url", "status"],
    columns_mapping: Dict[str, str] = {},
    labels_mapping: Dict[str, str] = {},
) -> None:
    gdown.download(gdown_link, output="zipped_dataset", quiet=True)
    dataset_path: str = unzip_file("zipped_dataset")
    df = pd.read_csv(dataset_path)

    if columns_mapping:
        df = df[columns].rename(columns=columns_mapping)
    if labels_mapping:
        df["label"] = df["label"].map(labels_mapping)

    if os.path.exists(target_file_path):
        df.to_csv(target_file_path, mode="a", index=False, header=False)
    else:
        df.to_csv(target_file_path, index=False)

    clean_up(["zipped_dataset", dataset_path])
