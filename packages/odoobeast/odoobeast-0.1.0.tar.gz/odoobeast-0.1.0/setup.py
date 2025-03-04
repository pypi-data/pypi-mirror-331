from setuptools import setup, find_packages

setup(
    name='odoobeast',
    version='0.1.0',
    description='OdooBeast: The ultimate AI-powered personal assistant library',
    author='Atharva Chourasia',
    author_email='harvestwithhellobro@gmail.com',
    url='https://github.com/MaybeHellobro/odoobeast',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
        'nltk>=3.6.0',
        'transformers>=4.6.0',
        'torch>=1.9.0',
        'tensorflow>=2.5.0',
        'spacy>=3.1.0',
        'flask>=2.0.1',
        'loguru>=0.5.3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
