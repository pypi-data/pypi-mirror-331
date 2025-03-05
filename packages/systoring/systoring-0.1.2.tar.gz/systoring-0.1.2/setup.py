from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="systoring",
    version="0.1.2",
    author="AtlasKunner",
    description="Кроссплатформенная библиотека для мониторинга системных событий | For Educational Purposes ONLY!!!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DGaliaf/systoring",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pynput>=1.7.6",
    ],
    extras_require={
        'windows': ["pywin32>=306"],
        'macos': ["pyobjc-framework-Cocoa>=9.2"],
    },
) 