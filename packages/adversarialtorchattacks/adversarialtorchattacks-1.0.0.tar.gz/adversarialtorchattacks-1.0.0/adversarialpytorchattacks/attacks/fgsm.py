import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

class FGSM:
    def __init__(self, model, epsilon=0.03):
        self.model = model
        self.epsilon = epsilon

    def generate(self, image, label):
        image.requires_grad = True
        output = self.model(image)
        loss = F.cross_entropy(output, label)
        self.model.zero_grad()
        loss.backward()
        perturbation = self.epsilon * image.grad.sign()
        adv_image = torch.clamp(image + perturbation, 0, 1)
        return adv_image, self.visualize_perturbation(perturbation)

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
