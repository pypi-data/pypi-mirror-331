import torch
import torch.nn.functional as F

class DeepFool:
    def __init__(self, model, steps=50, overshoot=0.02, num_classes=10):
        """
        DeepFool Attack Implementation.

        Args:
            model (torch.nn.Module): The target model.
            steps (int): Maximum number of iterations.
            overshoot (float): Controls the amount of perturbation.
            num_classes (int): Number of classes considered.
        """
        self.model = model
        self.steps = steps
        self.overshoot = overshoot
        self.num_classes = num_classes

    def __call__(self, images: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Generates adversarial examples using DeepFool.

        Args:
            images (torch.Tensor): Input images (batch, C, H, W).
            labels (torch.Tensor): True labels (not used in DeepFool directly).

        Returns:
            torch.Tensor: Perturbed images.
        """
        images = images.clone().detach().requires_grad_(True)
        original_images = images.clone().detach()

        batch_size = images.shape[0]
        perturbed_images = images.clone().detach()

        for i in range(batch_size):
            image = images[i: i + 1]  # Single image from batch
            image.requires_grad_(True)

            for _ in range(self.steps):
                logits = self.model(image)
                predicted_class = logits.argmax(dim=1).item()

                if predicted_class != labels[i].item():
                    break  # Stop if misclassified

                gradients = []
                for j in range(self.num_classes):
                    self.model.zero_grad()
                    logits[0, j].backward(retain_graph=True)

                    if image.grad is None:  # Fix: Ensure gradients are populated
                        raise RuntimeError("Gradient is None! Ensure image.requires_grad_() is set.")

                    gradients.append(image.grad.clone())  # Store cloned gradient

                gradients = torch.stack(gradients)

                # Compute perturbation (DeepFool method)
                diffs = gradients[1:] - gradients[0]
                norms = torch.norm(diffs.view(self.num_classes - 1, -1), dim=1)
                min_idx = torch.argmin(norms)
                r = (norms[min_idx] + 1e-6) * diffs[min_idx] / (torch.norm(diffs[min_idx]) + 1e-6)

                # Apply perturbation
                image = image.detach() + (1 + self.overshoot) * r.view(image.shape)
                image.requires_grad_(True)  # Re-enable gradients

            # Save the final perturbed image
            perturbed_images[i] = image.detach()

        return torch.clamp(perturbed_images, 0, 1)  # Ensure valid pixel values
