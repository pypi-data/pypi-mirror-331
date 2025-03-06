from setuptools import setup, find_packages

setup(
    name='fixout',
    version='0.1.12',
    description='Algorithmic inspection for trustworthy ML models',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
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