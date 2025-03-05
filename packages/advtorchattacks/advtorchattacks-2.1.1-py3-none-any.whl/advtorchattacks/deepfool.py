import torch
import torch.nn.functional as F

class DeepFool:
    def __init__(self, model, steps=50, overshoot=0.02, num_classes=10):
        self.model = model
        self.steps = steps
        self.overshoot = overshoot
        self.num_classes = num_classes

    def __call__(self, images, labels):
        # Ensure the input `images` is in the correct shape (4D)
        if images.ndim != 4:
            raise ValueError(f"Expected 4D input, but got {images.shape}. Ensure the input is [batch_size, channels, height, width].")
        
        # Clone and enable gradient tracking for images
        images = images.clone().detach().requires_grad_(True)
        perturbed_images = images.clone().detach()

        for _ in range(self.steps):
            # Perform forward pass
            logits = self.model(perturbed_images)
            
            # Get the predicted top class for each sample
            _, preds = logits.sort(descending=True)
            top_class = preds[:, 0]

            # Stop if the adversarial attack has succeeded
            if (top_class != labels).all():
                break

            # Compute gradients for each class
            gradients = []
            for i in range(self.num_classes):
                self.model.zero_grad()  # Clear previous gradients
                
                # Backpropagate logits of class `i`
                logits[:, i].sum().backward(retain_graph=True)
                gradients.append(perturbed_images.grad.clone())  # Clone the gradients
                
            gradients = torch.stack(gradients)  # Stack all gradients into a single tensor

            # Compute minimal perturbation
            perturbation = self._compute_perturbation(gradients)

            # Apply perturbation, detach to prevent graph buildup
            perturbed_images = (perturbed_images + self.overshoot * perturbation).detach()
            perturbed_images.requires_grad_()  # Re-enable gradient tracking

        return perturbed_images

    def _compute_perturbation(self, gradients):
        # Compute average perturbation across all class gradients
        perturbation = gradients.mean(dim=0)
        return perturbation.sign()  # Apply the sign function for minimal perturbation
