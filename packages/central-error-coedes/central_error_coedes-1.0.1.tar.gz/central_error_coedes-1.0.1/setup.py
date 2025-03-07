# setup.py

from setuptools import setup, find_packages

setup(
    name='central-error-coedes',  # Name of your package
    version='1.0.1',           # Version of your package
    description='A module to handle error codes loaded from JSON files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/error_code_module',  # URL of your project (e.g., GitHub)
    packages=find_packages(),  # Automatically find your package
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version
)
