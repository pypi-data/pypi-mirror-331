from setuptools import setup, find_packages

setup(
    name='fixout',
    version='0.1.01',
    description='Algorithmic inspection for trustworthy ML models',
    packages=find_packages(),
    install_requires=[
        'Flask==3.0.3',
        'Jinja2==3.1.4',
        'numpy==1.26.4',
        'pandas==2.2.3',
        'plotly==5.24.0',
        'scikit-image==0.24.0',
        'scikit-learn==1.5.2',
        'scipy==1.11.4',
        'thrift==0.20.0',
        'tinycss2==1.4.0',
        'webcolors==24.11.1'
    ]
)