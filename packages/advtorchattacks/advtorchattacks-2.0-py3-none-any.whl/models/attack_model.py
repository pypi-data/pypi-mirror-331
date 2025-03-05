import torch
import torch.nn as nn
import torchvision.models as models

class AttackModel:
    def __init__(self, model_name: str = "resnet18", pretrained: bool = False, device=None):
        """
        Initializes a model for attack testing.

        Args:
            model_name (str): Name of the model (default: resnet18).
            pretrained (bool): Load pretrained weights.
            device (str): "cuda" or "cpu". Defaults to auto-detect.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = getattr(models, model_name)(pretrained=pretrained).to(self.device)
        self.model.eval()  # Set to evaluation mode

    def predict(self, images: torch.Tensor):
        """Runs model inference and returns predictions."""
        images = images.to(self.device)
        with torch.no_grad():
            outputs = self.model(images)
        return outputs.argmax(dim=1)

if __name__ == "__main__":
    attack_model = AttackModel()
    print("✅ Model loaded successfully!")
