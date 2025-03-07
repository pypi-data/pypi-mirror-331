from setuptools import setup, find_packages

setup(
    name="picflip",
    version="0.1.0",
    description="Remove image backgrounds and convert them to PNG!",
    author="Divpreet Singh",
    author_email="divpreetsingh68@gmail.com",
    packages=find_packages(),
    install_requires=[
        "rembg",
        "Pillow",
        "cairosvg",
        "onnxruntime"
    ],
    entry_points={
        "console_scripts": [
            "picflip=picflip.cli:main"
        ]
    },
)
