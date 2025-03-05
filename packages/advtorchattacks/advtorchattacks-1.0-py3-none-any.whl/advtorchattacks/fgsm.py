import torch
import torch.nn as nn

class FGSM:
    def __init__(self, model: nn.Module, epsilon: float = 0.03):
        """
        Fast Gradient Sign Method (FGSM) attack.

        Args:
            model (nn.Module): The target model to attack.
            epsilon (float): The perturbation magnitude (default: 0.03).
        """
        self.model = model
        self.epsilon = epsilon
        self.model.eval()  # Set model to evaluation mode

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using FGSM.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        images = images.clone().detach().requires_grad_(True)
        
        # Forward pass
        outputs = self.model(images)
        loss = nn.CrossEntropyLoss()(outputs, labels)

        # Compute gradients
        self.model.zero_grad()
        loss.backward()
        grad_sign = images.grad.sign()

        # Create adversarial examples
        adv_images = images + self.epsilon * grad_sign
        adv_images = torch.clamp(adv_images, 0, 1)  # Ensure valid pixel range

        return adv_images.detach()
