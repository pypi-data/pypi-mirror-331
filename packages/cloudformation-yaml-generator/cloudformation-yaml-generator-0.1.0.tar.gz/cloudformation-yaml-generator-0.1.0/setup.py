from setuptools import setup, find_packages

setup(
    name="cloudformation-yaml-generator",
    version="0.1.0",
    author="amit p",
    author_email="amitpotdar31@example.com",
    description="A Python package to generate AWS CloudFormation YAML templates dynamically",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cloudformation-yaml-generator",
    packages=find_packages(),
    install_requires=["pyyaml"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
