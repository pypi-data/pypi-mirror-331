import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

class CW:
    def __init__(self, model, c=1, kappa=0, steps=1000, lr=0.01):
        self.model = model
        self.c = c
        self.kappa = kappa
        self.steps = steps
        self.lr = lr

    def generate(self, image, label):
        adv_image = image.clone().detach().requires_grad_(True)
        optimizer = torch.optim.Adam([adv_image], lr=self.lr)

        for _ in range(self.steps):
            output = self.model(adv_image)
            loss = self.c * F.cross_entropy(output, label) - self.kappa * torch.norm(adv_image - image)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            adv_image = torch.clamp(adv_image, 0, 1)

        return adv_image, self.visualize_perturbation(adv_image - image)

    def visualize_perturbation(self, perturbation):
        perturbation = perturbation.squeeze().detach().cpu().numpy()
        perturbation = (perturbation - perturbation.min()) / (perturbation.max() - perturbation.min() + 1e-8)
        perturbation = (perturbation * 255).astype(np.uint8)

        fig, ax = plt.subplots()
        ax.imshow(perturbation.transpose(1, 2, 0), cmap="inferno")
        ax.axis("off")
        fig.canvas.draw()
        img_array = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        return img_array
