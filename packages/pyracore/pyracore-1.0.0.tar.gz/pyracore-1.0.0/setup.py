# setup.py
from setuptools import setup, find_packages

setup(
    name="pyracore", 
    version="1.0.0",
    author="Joaquim Carlos Timóteo",  # Seu nome
    author_email="joaquimcarlostimoteo1@gmail.com",  # Seu e-mail
    description="Uma biblioteca modular para operações avançadas em sistemas.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joaquimtimoteo/pyracore",  # Atualize o link do repositório, se necessário
    packages=find_packages(),
    install_requires=[
        "cryptography",
        "pynput",
        "requests",
        "scapy",
        "psutil",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)