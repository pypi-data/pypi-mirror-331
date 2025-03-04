import torch
import matplotlib.pyplot as plt
import numpy as np
from torchvision.transforms import ToPILImage

def visualize_perturbation(original, adversarial, cmap="inferno", scale_factor=255):
    """
    Generate a visualization of the perturbation between original and adversarial images.
    
    Args:
        original (torch.Tensor): Original clean image.
        adversarial (torch.Tensor): Adversarial image.
        cmap (str): Colormap to use for visualization.
        scale_factor (int): Scaling factor to enhance visibility.
    
    Returns:
        torch.Tensor: Perturbation visualization as an image.
    """
    perturbation = adversarial - original
    perturbation = (perturbation - perturbation.min()) / (perturbation.max() - perturbation.min() + 1e-8)
    perturbation = perturbation * scale_factor  # Scale for better visibility
    
    perturbation_np = perturbation.squeeze().detach().cpu().numpy()

    # Plot the perturbation
    fig, ax = plt.subplots()
    ax.imshow(perturbation_np.transpose(1, 2, 0).astype("uint8"), cmap=cmap)
    ax.axis("off")

    # Save figure to an array
    fig.canvas.draw()
    img_array = np.array(fig.canvas.renderer.buffer_rgba())

    plt.close(fig)  # Close the figure to avoid display issues

    # Convert back to tensor
    perturbation_tensor = torch.tensor(img_array).permute(2, 0, 1).float() / 255.0
    return perturbation_tensor

def save_image(tensor, filename):
    """
    Save a PyTorch tensor as an image.

    Args:
        tensor (torch.Tensor): Image tensor.
        filename (str): Output file name.
    """
    image = ToPILImage()(tensor.squeeze(0))
    image.save(filename)
    print(f"Saved image: {filename}")
