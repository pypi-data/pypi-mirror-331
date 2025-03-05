# setup.py
from setuptools import setup, find_packages

setup(
    name="videofacecapture",
    version="0.1.0",
    author="Nazir Umar",
    author_email="nazirumar888@gmail.com",
    description="A library to capture faces from videos and images using OpenCV",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nazirumar/videofacecapture",  # Optional
    packages=find_packages(),
    install_requires=["opencv-python>=4.5.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)