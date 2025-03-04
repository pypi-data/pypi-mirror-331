from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="image_similarity_core",  # More specific name
    version="0.1.0",
    author="Ambati Rajendra",
    author_email="rajendraambati.ai@gmail.com",
    description="A package to find the reference ID of the most similar image using ResNet50 and cosine similarity.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/palm_image_similarity",  # Update with your actual repository
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",  # Specify minimum versions
        "pandas>=1.1.0",
        "Pillow>=8.0.0",
        "scikit-learn>=0.23.0",
        "torch>=1.7.0",
        "torchvision>=0.8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose appropriate license
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.6",
)