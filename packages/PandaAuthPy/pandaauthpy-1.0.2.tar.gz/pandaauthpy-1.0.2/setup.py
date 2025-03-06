from setuptools import setup, find_packages

setup(
    name="PandaAuthPy",
    version="1.0.2",
    packages=find_packages(),
    install_requires=["requests"],
    author="Rice Jay",
    author_email="yvor.exe@example.com",
    description="A Panda-Auth library for Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PandaAuthPy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
