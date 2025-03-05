import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class CW:
    def __init__(self, model: nn.Module, c: float = 1e-4, kappa: float = 0, steps: int = 1000, lr: float = 0.01):
        """
        Carlini & Wagner (CW) L2 attack.

        Args:
            model (nn.Module): The target model to attack.
            c (float): Confidence coefficient for optimization.
            kappa (float): Confidence margin (default: 0).
            steps (int): Number of optimization steps.
            lr (float): Learning rate for optimization.
        """
        self.model = model
        self.c = c
        self.kappa = kappa
        self.steps = steps
        self.lr = lr
        self.model.eval()  # Set model to evaluation mode

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using CW attack.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        batch_size = images.shape[0]
        device = images.device

        # Initialize adversarial perturbation (w), using tanh-space transformation
        w = torch.zeros_like(images, requires_grad=True, device=device)
        optimizer = optim.Adam([w], lr=self.lr)

        # Convert images to tanh-space
        tanh_images = 0.5 * (torch.tanh(images) + 1)

        for _ in range(self.steps):
            adv_images = 0.5 * (torch.tanh(w) + 1)  # Convert w back to image-space
            outputs = self.model(adv_images)

            # Compute loss function: L2 distortion + classification loss
            l2_dist = torch.norm(adv_images - tanh_images, p=2, dim=(1, 2, 3))
            one_hot_labels = F.one_hot(labels, num_classes=outputs.shape[1]).float()
            correct_logits = torch.sum(one_hot_labels * outputs, dim=1)
            wrong_logits, _ = torch.max(outputs * (1 - one_hot_labels) - 1e4 * one_hot_labels, dim=1)
            f_loss = torch.clamp(correct_logits - wrong_logits + self.kappa, min=0)

            loss = self.c * f_loss + l2_dist
            optimizer.zero_grad()
            loss.mean().backward()
            optimizer.step()

        # Return adversarial examples
        return adv_images.detach()
