from setuptools import setup, find_packages

setup(
    name='fixout',
    version='0.1.14',
    description='Algorithmic inspection for trustworthy ML models',
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fixouttech/fixout",
    author="FixOut",
    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.12.9",
)