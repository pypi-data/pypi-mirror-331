import torch
import torch.nn.functional as F
from typing import Any

from ..model import PhisherModel


class GradCAM:
    def __init__(self: "GradCAM", model: PhisherModel, target_layer: Any) -> None:
        self.model: PhisherModel = model
        self.target_layer: Any = target_layer
        self.gradients = None
        self.activations = None

        self.hook_forward()
        self.hook_backward()

    def hook_forward(self: "GradCAM") -> None:
        def forward_hook(_, __, output):
            self.activations = output

        self.target_layer.register_forward_hook(forward_hook)

    def hook_backward(self: "GradCAM") -> None:
        def backward_hook(_, __, grad_output):
            self.gradients = grad_output[0]

        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(
        self: "GradCAM", input_tensor: torch.Tensor, target_class: torch.Tensor
    ) -> torch.Tensor:
        output = self.model(input_tensor)

        self.model.zero_grad()
        target = output[:, target_class]
        target.backward()

        gradients = self.gradients
        activations = self.activations

        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)

        cam = torch.sum(weights * activations, dim=1)
        cam = F.relu(cam)

        return (cam - cam.min()) / cam.max()
