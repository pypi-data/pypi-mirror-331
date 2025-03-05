import torch
import torch.nn as nn

class PGD:
    def __init__(self, model, epsilon=0.03, alpha=0.01, steps=10):
        """
        Initializes the PGD attack.

        Args:
            model (torch.nn.Module): Target model.
            epsilon (float): Maximum perturbation.
            alpha (float): Step size.
            steps (int): Number of attack iterations.
        """
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps
        self.loss_fn = nn.CrossEntropyLoss()

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using PGD.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        images = images.clone().detach().to(torch.float32)  # Ensure tensor is a leaf tensor
        labels = labels.to(images.device)
        original_images = images.clone().detach()

        for _ in range(self.steps):
            images.requires_grad_(True)  
            images.retain_grad()  # ✅ Ensure gradients are retained

            # Forward pass
            outputs = self.model(images)
            loss = self.loss_fn(outputs, labels)

            # Compute gradients
            self.model.zero_grad()
            loss.backward()

            if images.grad is None:  # Debugging check
                raise RuntimeError("Gradient is None! Ensure model & inputs require grads.")

            # Compute perturbation and apply step
            grad_sign = images.grad.sign()
            images = images.detach() + self.alpha * grad_sign  # Perform step

            # Clip perturbation to stay within epsilon ball
            perturbation = torch.clamp(images - original_images, min=-self.epsilon, max=self.epsilon)
            images = torch.clamp(original_images + perturbation, min=0, max=1).detach()

        return images
