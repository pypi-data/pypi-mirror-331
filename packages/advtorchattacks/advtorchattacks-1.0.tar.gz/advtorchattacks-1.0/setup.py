from setuptools import setup, find_packages

setup(
    name="advtorchattacks",
    version="1.0",
    author="Santhoshkumar K",
    author_email="santhoshatwork17@gmail.com",
    description="A PyTorch library for adversarial attacks, inspired by torchattacks.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/santhos1705kumar/advtorchattacks",
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
