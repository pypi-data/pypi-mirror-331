import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

class PGD:
    def __init__(self, model, epsilon=0.03, alpha=0.005, steps=10):
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps

    def generate(self, image, label):
        adv_image = image.clone().detach().requires_grad_(True)
        for _ in range(self.steps):
            output = self.model(adv_image)
            loss = F.cross_entropy(output, label)
            self.model.zero_grad()
            loss.backward()
            perturbation = self.alpha * adv_image.grad.sign()
            adv_image = adv_image + perturbation
            adv_image = torch.clamp(adv_image, image - self.epsilon, image + self.epsilon)
            adv_image = torch.clamp(adv_image, 0, 1)
        return adv_image, self.visualize_perturbation(adv_image - image)

    def visualize_perturbation(self, perturbation):
        perturbation = perturbation.squeeze().detach().cpu().numpy()
        perturbation = (perturbation - perturbation.min()) / (perturbation.max() - perturbation.min() + 1e-8)
        perturbation = (perturbation * 255).astype(np.uint8)

        fig, ax = plt.subplots()
        ax.imshow(perturbation.transpose(1, 2, 0), cmap="plasma")
        ax.axis("off")
        fig.canvas.draw()
        img_array = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        return img_array
