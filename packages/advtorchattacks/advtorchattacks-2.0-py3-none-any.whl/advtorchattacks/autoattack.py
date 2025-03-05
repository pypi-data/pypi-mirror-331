import torch
import torch.nn as nn
from .pgd import PGD
from .deepfool import DeepFool
from .mifgsm import MIFGSM

class AutoAttack:
    def __init__(self, model: nn.Module, epsilon: float = 0.03, steps: int = 40):
        """
        AutoAttack: An ensemble attack combining multiple strong attacks.

        Args:
            model (nn.Module): The target model to attack.
            epsilon (float): Maximum perturbation allowed.
            steps (int): Number of attack iterations (for iterative attacks).
        """
        self.model = model
        self.epsilon = epsilon
        self.steps = steps
        self.model.eval()  # Set model to evaluation mode

        # Initialize sub-attacks
        self.attacks = [
            PGD(model, epsilon=self.epsilon, alpha=self.epsilon / 10, steps=self.steps),
            DeepFool(model, steps=self.steps),
            MIFGSM(model, epsilon=self.epsilon, alpha=self.epsilon / 10, steps=self.steps)
        ]

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using multiple attacks and selects the strongest.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        best_adv_images = images.clone().detach()
        max_confidence = torch.zeros(images.shape[0]).to(images.device)  # Track highest misclassification confidence

        for attack in self.attacks:
            adv_images = attack(images, labels)  # Apply attack
            outputs = self.model(adv_images)
            confidence, preds = torch.max(outputs, dim=1)

            # Select the adversarial example with the highest confidence misclassification
            mask = preds != labels  # Check which images are misclassified
            update_mask = mask & (confidence > max_confidence)
            max_confidence[update_mask] = confidence[update_mask]
            best_adv_images[update_mask] = adv_images[update_mask]

        return best_adv_images.detach()
