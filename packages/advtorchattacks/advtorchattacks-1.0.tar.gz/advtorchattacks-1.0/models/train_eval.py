import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
from advtorchattacks.models.attack_model import AttackModel
from advtorchattacks.advtorchattacks.fgsm import FGSM

# Load dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
train_dataset = datasets.MNIST(root="./data", train=True, transform=transform, download=True)
test_dataset = datasets.MNIST(root="./data", train=False, transform=transform, download=True)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Load model
model = AttackModel(model_name="resnet18", pretrained=False).model
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
def train(model, train_loader, epochs=1):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for images, labels in train_loader:
            images, labels = images.to(model.device), labels.to(model.device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {total_loss / len(train_loader)}")

# Evaluate robustness
def evaluate(model, test_loader):
    model.eval()
    correct, total = 0, 0
    fgsm = FGSM(model, epsilon=0.03)

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(model.device), labels.to(model.device)
            adv_images = fgsm(images, labels)
            preds = model(adv_images).argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    print(f"Accuracy on FGSM adversarial examples: {100 * correct / total:.2f}%")

if __name__ == "__main__":
    train(model, train_loader, epochs=1)
    evaluate(model, test_loader)
