## 📦 Installation
Install the package via pip:
```sh
pip install adversarialpytorchattack

## 📦 Or installation using Github 
Or install from source
```sh
git clone https://github.com/santhoshatwork17@gmail.com/adversarialpytorchattackers.git
cd adversarial_pytorch_attack


## 🛠️ Usage
```python
import torch
import torchvision.models as models
from adversarialpytorchattack.attacks import FGSM, PGD, CW
from adversarialpytorchattack.utils import visualize_perturbation, save_image

# pre-trained model
model = models.resnet18(pretrained=True).eval()

# input image
image = torch.rand((1, 3, 224, 224))  # Example input
label = torch.tensor([0])  # Example label

# Apply attack
fgsm_attack = FGSM(model, epsilon=0.03)
adv_image = fgsm_attack(image, label)

# Save the adversarial image
save_image(adv_image, "adv_fgsm.jpg")
