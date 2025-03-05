import torch
import torch.nn as nn
import torch.nn.functional as F

class DeepFool:
    def __init__(self, model: nn.Module, steps: int = 50, overshoot: float = 0.02):
        """
        DeepFool attack for generating minimal perturbations.

        Args:
            model (nn.Module): The target model to attack.
            steps (int): Maximum number of iterations.
            overshoot (float): Factor to push the perturbation slightly outside the decision boundary.
        """
        self.model = model
        self.steps = steps
        self.overshoot = overshoot
        self.model.eval()  # Set model to evaluation mode

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using DeepFool.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): Corresponding labels.

        Returns:
            torch.Tensor: Perturbed images.
        """
        images = images.clone().detach().requires_grad_(True)
        batch_size = images.shape[0]
        device = images.device
        perturbed_images = images.clone().detach()

        for i in range(batch_size):
            image = images[i : i + 1]  # Process one image at a time
            perturbation = torch.zeros_like(image).to(device)

            for _ in range(self.steps):
                image.requires_grad_(True)
                outputs = self.model(image)
                _, predicted_label = torch.max(outputs, 1)

                if predicted_label != labels[i]:  # Stop if misclassified
                    break

                gradients = []
                logits = outputs.squeeze()
                for j in range(logits.shape[0]):  # Compute gradient for each class
                    self.model.zero_grad()
                    logits[j].backward(retain_graph=True)
                    gradients.append(image.grad.clone())

                gradients = torch.stack(gradients)
                logits_diff = logits - logits[labels[i]]
                logits_diff[labels[i]] = float("inf")  # Ignore correct class

                # Compute minimal perturbation to cross decision boundary
                min_idx = torch.argmin(torch.abs(logits_diff))
                w = gradients[min_idx] - gradients[labels[i]]
                r_i = torch.abs(logits_diff[min_idx]) / (torch.norm(w) + 1e-6) * w

                perturbation += r_i
                image = (images[i] + (1 + self.overshoot) * perturbation).detach()

            perturbed_images[i] = image

        return torch.clamp(perturbed_images, 0, 1)  # Ensure valid range
