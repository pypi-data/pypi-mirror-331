from setuptools import setup, find_packages

setup(
    name="blackspammerbd_one",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bsb=blackspammerbd_one.cli:main",
        ],
    },
    install_requires=[
        "colorama"
    ],
    author="Shawpon Sp",
    author_email="shawponsp6@gmail.com",
    description="CLI package for device connection and file transfer",
    url="https://github.com/yourusername/blackspammerbd_one",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
