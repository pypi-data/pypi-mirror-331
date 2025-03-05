import torch
import torch.nn as nn

class PGD:
    def __init__(self, model: nn.Module, epsilon: float = 0.03, alpha: float = 0.01, steps: int = 40):
        """
        Projected Gradient Descent (PGD) attack.

        Args:
            model (nn.Module): The target model to attack.
            epsilon (float): The maximum perturbation.
            alpha (float): Step size per iteration.
            steps (int): Number of attack iterations.
        """
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps
        self.model.eval()  # Set model to evaluation mode

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using PGD.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        images = images.clone().detach()
        original_images = images.clone().detach()

        for _ in range(self.steps):
            images.requires_grad_(True)

            # Forward pass
            outputs = self.model(images)
            loss = nn.CrossEntropyLoss()(outputs, labels)

            # Compute gradients
            self.model.zero_grad()
            loss.backward()
            grad_sign = images.grad.sign()

            # Apply perturbation and project within epsilon ball
            images = images + self.alpha * grad_sign
            images = torch.max(torch.min(images, original_images + self.epsilon), original_images - self.epsilon)
            images = torch.clamp(images, 0, 1)  # Keep in valid range

        return images.detach()
