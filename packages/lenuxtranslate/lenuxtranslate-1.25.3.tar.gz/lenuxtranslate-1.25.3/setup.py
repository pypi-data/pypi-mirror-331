from setuptools import setup, find_packages

setup(
    name="lenuxtranslate",
    version="1.25.3",
    author="razzy-code",
    author_email="nsaylan0@gmail.com",
    description="Argos Translate Tabanlı Türkçe Destekli Çeviri Kütüphanesi",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/razzy-code/lenuxtranslatee",
    packages=find_packages(),
    install_requires=[
        "argostranslate",
        "colorama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "lenuxtranslate=lenuxtranslate.main:main"
        ],
    },
)
