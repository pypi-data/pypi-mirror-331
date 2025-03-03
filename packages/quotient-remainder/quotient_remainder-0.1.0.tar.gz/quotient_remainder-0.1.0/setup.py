from setuptools import setup, find_packages

setup(
    name="quotient_remainder",
    version="0.1.0",
    author='Arthur S., John "Soap Ultra" MacTavish',
    author_email="aprofileforwriting@gmail.com, excaliburpendragonii@gmail.com",
    description="A package for finding remainders and quotients.",
    long_description=open("README.md").read(),  # Long description (usually from README)
    long_description_content_type="text/markdown",
    url="https://github.com/DeFiDegenDude/Quotient-Remainder",
    packages=find_packages(),
    classifiers=[ 
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",
)
