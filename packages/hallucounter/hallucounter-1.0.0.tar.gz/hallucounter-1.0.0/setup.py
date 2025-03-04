import setuptools

from setuptools import setup, find_packages
with open('/content/README.md','r') as f:
    description=f.read()
setup(
    name="hallucounter",
    version="1.0.0",
    # author="Your Name",
    # author_email="your.email@example.com",
    description="A tool for reference-free hallucination detection in LLM-generated responses",
    packages=find_packages(),
    install_requires=open("/content/requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
)
