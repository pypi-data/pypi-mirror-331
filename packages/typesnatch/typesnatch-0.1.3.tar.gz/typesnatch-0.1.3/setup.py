from setuptools import setup, find_packages

# Read dependencies from requirements.txt
def read_requirements():
    with open("requirements.txt") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name='typesnatch',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'click',
        'colorama',
        'playwright',
        'requests',
        'inquirer',
    ],
    entry_points={
        'console_scripts': [
            'typesnatch=typesnatch.cli:cli',
        ],
    },
    author='Brandon Fryslie',
    author_email='admin@swank.town',
    description='TypeSnatch: Install fonts the easy way',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/brandon-fryslie/typesnatch',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
