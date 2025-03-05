import torch
import torch.nn as nn
import torch.nn.functional as F

class MIFGSM:
    def __init__(self, model: nn.Module, epsilon: float = 0.03, alpha: float = 0.01, steps: int = 10, decay: float = 1.0):
        """
        Momentum Iterative Fast Gradient Sign Method (MI-FGSM) attack.

        Args:
            model (nn.Module): The target model to attack.
            epsilon (float): The maximum perturbation allowed.
            alpha (float): The step size for each iteration.
            steps (int): Number of attack iterations.
            decay (float): Decay factor for momentum.
        """
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps
        self.decay = decay
        self.model.eval()  # Set model to evaluation mode

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using MI-FGSM.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        images = images.clone().detach()
        original_images = images.clone().detach()
        momentum = torch.zeros_like(images)

        for _ in range(self.steps):
            images.requires_grad_(True)
            outputs = self.model(images)
            loss = F.cross_entropy(outputs, labels)

            # Compute gradients
            self.model.zero_grad()
            loss.backward()
            grad = images.grad

            # Apply momentum
            grad = grad / torch.mean(torch.abs(grad), dim=(1, 2, 3), keepdim=True)
            momentum = self.decay * momentum + grad

            # Apply attack step
            images = images + self.alpha * momentum.sign()
            images = torch.max(torch.min(images, original_images + self.epsilon), original_images - self.epsilon)
            images = torch.clamp(images, 0, 1)  # Ensure valid pixel range

        return images.detach()
