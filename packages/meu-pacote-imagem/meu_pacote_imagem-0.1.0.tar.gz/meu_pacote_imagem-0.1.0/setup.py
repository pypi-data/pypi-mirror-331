
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="meu_pacote_imagem",
    version="0.1.0",
    author="David Miranda",
    author_email="mirandadavid2021@gmail.com",
    description="Um pacote para processamento de imagens",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Miiranda0/meu_pacote_imagem",
    packages=find_packages(),
    install_requires=["Pillow"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
