from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="bergcastro_image_processing",  
    version="0.1.3", 
    author="Lindemberg Castro",  
    author_email="lindembergncastro@outlook.com", 
    description="Pacote de processamento de imagens", 
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    url="https://github.com/BergCastro/image-processing-package",  
    packages=find_packages(),  
    install_requires=requirements,
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',  
)