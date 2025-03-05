from setuptools import setup, find_packages

setup(
    name='ligraph',
    version='0.1.0',
    author='Ali Ahammad',
    author_email='mail@aliahammad.com',
    description='A Python package for graph data structures and algorithms.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ligraph',  # Replace with your actual GitHub repository
    packages=find_packages(),
    install_requires=[
        # No external dependencies required
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ],
    python_requires='>=3.6',
)