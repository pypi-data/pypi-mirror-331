from setuptools import setup, find_packages

setup(
    name="kurzaj",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "kurzaj=kurzajpackage.main:kurzaj",
        ],
    },
    author="kurzaj",
    description="Kurzaj",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://example.com/",  # Replace with your GitHub
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
