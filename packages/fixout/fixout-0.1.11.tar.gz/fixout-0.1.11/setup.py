from setuptools import setup, find_packages

setup(
    name='fixout',
    version='0.1.11',
    description='Algorithmic inspection for trustworthy ML models',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fixouttech/fixout",
    packages=find_packages(),
    python_requires=">=3.12.9",
)