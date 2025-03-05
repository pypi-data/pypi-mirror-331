import torch
import torch.nn as nn
import torch.nn.functional as F

class MIFGSM:
    def __init__(self, model, epsilon=0.03, alpha=0.01, steps=10, decay=1.0):
        """
        Momentum Iterative Fast Gradient Sign Method (MI-FGSM) attack.
        
        Args:
            model (nn.Module): Target model.
            epsilon (float): Perturbation limit.
            alpha (float): Step size per iteration.
            steps (int): Number of attack iterations.
            decay (float): Decay factor for momentum term.
        """
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps
        self.decay = decay
    
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
            images.requires_grad = True  # Enable gradient tracking
            outputs = self.model(images)
            loss = F.cross_entropy(outputs, labels)

            self.model.zero_grad()
            loss.backward()
            
            if images.grad is None:
                raise RuntimeError("Gradients are not being computed. Check if requires_grad is set correctly.")

            grad = images.grad.clone().detach()
            grad = grad / (torch.mean(torch.abs(grad), dim=(1, 2, 3), keepdim=True) + 1e-8)  # Normalize
            momentum = self.decay * momentum + grad  # Apply momentum
            images = images + self.alpha * momentum.sign()
            images = torch.clamp(images, original_images - self.epsilon, original_images + self.epsilon)  # Clip perturbation
            images = torch.clamp(images, 0, 1).detach()  # Keep within valid image range

        return images