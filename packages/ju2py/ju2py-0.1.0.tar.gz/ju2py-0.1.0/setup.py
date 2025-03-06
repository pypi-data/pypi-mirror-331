from setuptools import setup, find_packages

setup(
    name="ju2py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["nbformat", "nbconvert", "twine"],
    entry_points={
        "console_scripts": [
            "j2p=j2p.cli:main",
        ],
    },
    author="Abolfazl Ziaeemehr",
    author_email="a.ziaeemehr@gmail.com",
    description="A simple tool to convert Jupyter notebooks to Python scripts.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ziaeemehr/ju2py",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
