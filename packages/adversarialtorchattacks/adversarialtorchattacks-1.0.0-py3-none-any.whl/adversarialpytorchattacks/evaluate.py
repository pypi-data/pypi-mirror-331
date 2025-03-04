from .attacks import FGSM, PGD, CW, MIFGSM, AutoAttack

def evaluate(model, image, label):
    """
    Evaluates a model by applying multiple adversarial attacks.

    Args:
        model (torch.nn.Module): The neural network model.
        image (torch.Tensor): The input image.
        label (torch.Tensor): The true label of the image.

    Returns:
        dict: Dictionary containing adversarial images and perturbations for each attack.
    """
    model.eval()  # Ensure model is in evaluation mode

    # Initialize attacks
    fgsm = FGSM(model)
    pgd = PGD(model)
    cw = CW(model)
    mifgsm = MIFGSM(model)
    autoattack = AutoAttack(model)

    # Generate adversarial examples
    fgsm_img, fgsm_perturbation = fgsm.generate(image, label)
    pgd_img, pgd_perturbation = pgd.generate(image, label)
    cw_img, cw_perturbation = cw.generate(image, label)
    mifgsm_img, mifgsm_perturbation = mifgsm.generate(image, label)
    autoattack_img, autoattack_perturbation = autoattack.generate(image, label)

    return {
        "FGSM": (fgsm_img, fgsm_perturbation),
        "PGD": (pgd_img, pgd_perturbation),
        "CW": (cw_img, cw_perturbation),
        "MIFGSM": (mifgsm_img, mifgsm_perturbation),
        "AutoAttack": (autoattack_img, autoattack_perturbation),
    }
