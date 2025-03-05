from setuptools import setup, find_packages

setup(
    name="expab",
    version="0.0.1",
    url='https://github.com/Renarion/AB_library',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Renat/Egor",
    author_email="ryunisov0@gmail.com",
    description="A comprehensive Python library for A/B testing analysis",
    classifiers=[
        'Intended Audience :: Science/Research', 
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3',  
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=[
        'numpy>=1.18.0',
        'pandas>=1.0.0',
        'matplotlib>=3.0.0',
        'scipy>=1.4.0',
        'statsmodels>=0.12.0',
        'seaborn>=0.11.0', 
        'tqdm>=4.0.0', 
    ],
)
