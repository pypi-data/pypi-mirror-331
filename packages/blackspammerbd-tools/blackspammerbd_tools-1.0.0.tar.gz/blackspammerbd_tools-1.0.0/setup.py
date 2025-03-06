from setuptools import setup, find_packages

setup(
    name="blackspammerbd_tools",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bsb=blackspammerbd_tools.cli:main",
        ],
    },
    install_requires=[
        "colorama"
    ],
    author="Shawpon Sp",
    author_email="shawponsp6@gmail.com",
    description="A CLI package for secure device connection and file transfer",
    url="https://github.com/BlackSpammerBd/blackspammerbd_tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
