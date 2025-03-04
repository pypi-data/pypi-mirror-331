from setuptools import setup, find_packages

setup(
    name="adversarialtorchattacks",
    version="1.0.0",
    author="Santhoshkumar K",
    author_email="santhoshatwork17@gmail.com",
    description="A PyTorch package for adversarial attacks (FGSM, PGD, CW, MIFGSM, AutoAttack) with visualization.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/santhosh1705kumar/adversarialpytorchattackers",
    # license="MIT",
    packages=find_packages(),
    install_requires=[
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "matplotlib>=3.4.0",
        "numpy>=1.19.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
)
