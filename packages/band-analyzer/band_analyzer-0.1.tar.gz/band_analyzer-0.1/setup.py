from setuptools import setup, find_packages

setup(
    name="band_analyzer",
    version="0.1",
    packages=["band_analyzer"], 
    package_dir={"band_analyzer": "band_analyzer"},
    install_requires=["numpy",
        "opencv-python",
        "pandas",
        "scipy"],
    author="Egwer David Sierra Jaraba",
    description="Un paquete para analizar bandas de electroforesis",
    #long_description=open("README.md").read(),
    #long_description_content_type="text/markdown",
    url="https://github.com/esierraj/electrophoresis_analysis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
        ],
)

