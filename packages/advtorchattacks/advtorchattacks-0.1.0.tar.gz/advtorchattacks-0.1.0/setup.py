from setuptools import setup, find_packages

setup(
    name="advtorchattacks",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A PyTorch library for adversarial attacks, inspired by torchattacks.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/advtorchattacks",
    packages=find_packages(),
    install_requires=[
        "torch>=1.8.0",
        "torchvision",
        "numpy",
        "scipy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
)
