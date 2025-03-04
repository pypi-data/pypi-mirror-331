
from setuptools import setup, find_packages

setup(
    name='classWeightLearn',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'scikit-learn==1.6.1',
        'sdv==1.18.0',
        'pandas==2.0.3',
        'optuna==4.2.0'
        # Add any dependencies your package needs
    ],
    author='Mahayasa Adiputra',
    author_email='mahayasa.a@kkumail.com',
    description='Optuna Class Weight Cost-Sensitive Learning',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    license='',
)