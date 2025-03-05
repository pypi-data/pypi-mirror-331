from setuptools import setup, find_packages

setup(
    name="alphamorph",
    version="0.4",
    author="David Fernandez Bonet",
    author_email="davferdz@gmail.com",
    description="Morph point clouds into circular shapes using alpha shapes and thin-plate splines.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DavidFernandezBonet/alphamorph",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "alphashape",
        "scipy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
