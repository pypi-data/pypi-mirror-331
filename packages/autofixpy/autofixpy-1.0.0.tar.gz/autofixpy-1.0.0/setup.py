from setuptools import setup, find_packages

setup(
    name="autofixpy",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "autofixpy=autofixpy.cli:main",
        ],
    },
    author="Amogh Pathak",
    description="Automatically fixes Python errors",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
