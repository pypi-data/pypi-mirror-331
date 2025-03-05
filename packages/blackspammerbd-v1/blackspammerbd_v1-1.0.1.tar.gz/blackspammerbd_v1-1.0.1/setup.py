from setuptools import setup, find_packages

setup(
    name="blackspammerbd_v1",
    version="1.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bsb=blackspammerbd_v1.cli:main",
        ],
    },
    install_requires=[
        "colorama"
    ],
    author="Shawpon Sp",
    author_email="shawponsp6@gmail.com",
    description="A CLI package for device connection and file transfer",
    url="https://github.com/yourusername/blackspammerbd_v1",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
