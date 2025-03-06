import numpy as np
import torch
from typing import List, Tuple
from lime.lime_text import LimeTextExplainer
from lime.explanation import Explanation

from ..model import PhisherEmbeddingModel
from ..dataset import PhishingEmbeddingDataset


class PhisherModelWrapper:
    def __init__(
        self: "PhisherModelWrapper",
        model: PhisherEmbeddingModel,
        dataset: PhishingEmbeddingDataset,
        device: str,
    ):
        self.model = model
        self.dataset = dataset
        self.device = device

    def predict(self: "PhisherModelWrapper", urls: List[str]) -> np.ndarray:
        encoded_inputs: List[torch.Tensor] = [
            self.dataset.pad_or_trim(self.dataset.parse_url(url)) for url in urls
        ]
        input_tensor: torch.Tensor = torch.tensor(encoded_inputs, dtype=torch.long).to(
            self.device
        )

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = torch.sigmoid(outputs).cpu().numpy()

        return np.hstack([1 - probs, probs])


class LimePhisherExplainer:
    def __init__(
        self: "LimePhisherExplainer",
        model: PhisherEmbeddingModel,
        dataset: PhishingEmbeddingDataset,
        class_names: List[str],
        device: str = "cpu",
    ) -> None:
        self.wrapper: PhisherModelWrapper = PhisherModelWrapper(model, dataset, device)
        self.explainer = LimeTextExplainer(
            char_level=True, bow=False, class_names=class_names
        )

    def explain_url(
        self: "LimePhisherExplainer",
        url: str,
        labels: Tuple[int, int] = (0, 1),
        num_samples: int = 1000,
    ) -> Explanation:
        explanation = self.explainer.explain_instance(
            text_instance=url,
            classifier_fn=self.wrapper.predict,
            labels=labels,
            num_features=len(url),
            num_samples=num_samples,
        )
        return explanation
