from setuptools import setup, find_packages

setup(
    name='intelliops-sdk',
    version='0.1.0',
    author='Kodez',
    author_email='your.email@example.com',
    description='A Python SDK for IntelliOps',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/intelliops-sdk',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pydantic==2.10.6'
    ],
)