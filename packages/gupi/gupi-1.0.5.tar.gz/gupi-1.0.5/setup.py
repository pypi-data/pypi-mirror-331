from setuptools import setup, find_packages

setup(
    name="gupi",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "gupi = gupi.cli:main",  # Lệnh `mycli` sẽ gọi hàm `main` trong `cli.py`
        ],
    },
    author="Dao Le Bao Minh",
    author_email="djnner@proton.me",
    description="Dependency analyser for my future Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GlowCheese/gupi",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
