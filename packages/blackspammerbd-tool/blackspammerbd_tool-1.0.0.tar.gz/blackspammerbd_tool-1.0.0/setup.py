from setuptools import setup, find_packages

setup(
    name="blackspammerbd_tool",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bsb=blackspammerbd_tool.cli:main",
        ],
    },
    install_requires=[
        "colorama",
        "requests"
    ],
    author="Shawpon Sp",
    author_email="shawponsp6@gmail.com",
    description="A CLI package for secure device connection and file transfer",
    url="https://github.com/Blackspammerbd/blackspammerbd_tool",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
