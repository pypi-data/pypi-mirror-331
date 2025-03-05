from setuptools import setup, find_packages

setup(
    name="pyracore",
    version="3.0.0",  # Atualizado para a nova versão
    author="Joaquim Carlos Timóteo",
    author_email="joaquimcarlostimoteo1@gmail.com",
    description="Uma biblioteca modular para operações avançadas em sistemas.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joaquimtimoteo/pyracore",  # Atualize com o link do repositório GitHub
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