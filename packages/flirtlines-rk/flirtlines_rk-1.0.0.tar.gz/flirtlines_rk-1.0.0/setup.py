from setuptools import setup, find_packages

setup(
    name="flirtlines-rk",
    version="1.0.0",
    author="raayan",
    author_email="your.email@example.com",
    description="A Python package that gives random flirty lines.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flirtlines",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
