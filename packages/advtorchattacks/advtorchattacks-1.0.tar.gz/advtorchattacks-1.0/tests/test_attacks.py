import torch
import torchvision.models as models
from advtorchattacks.fgsm import FGSM
from advtorchattacks.pgd import PGD
from advtorchattacks.cw import CW
from advtorchattacks.deepfool import DeepFool
from advtorchattacks.mifgsm import MIFGSM
from advtorchattacks.autoattack import AutoAttack

def test_all_attacks():
    model = models.resnet18(pretrained=False)  # Simple model for testing
    model.eval()

    # Generate random input data
    images = torch.rand((2, 3, 224, 224))  # Batch of 2 images
    labels = torch.tensor([0, 1])  # Fake labels

    # List of attacks
    attacks = {
        "FGSM": FGSM(model, epsilon=0.03),
        "PGD": PGD(model, epsilon=0.03, alpha=0.01, steps=10),
        "CW": CW(model, steps=10, c=1.0),
        "DeepFool": DeepFool(model, steps=10),
        "MI-FGSM": MIFGSM(model, epsilon=0.03, alpha=0.01, steps=10, decay=1.0),
        "AutoAttack": AutoAttack(model, epsilon=0.03, steps=10)
    }

    for name, attack in attacks.items():
        adv_images = attack(images, labels)

        assert adv_images.shape == images.shape, f"{name} output shape mismatch!"
        assert torch.all((adv_images >= 0) & (adv_images <= 1)), f"{name} generated invalid pixel values!"

    print("✅ All attack tests passed!")

if __name__ == "__main__":
    test_all_attacks()
