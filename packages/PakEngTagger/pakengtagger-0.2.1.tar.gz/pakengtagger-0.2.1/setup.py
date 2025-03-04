from setuptools import setup, find_packages

setup(
    name='PakEngTagger',
    version='0.2.1',
    packages=find_packages(),  # Automatically finds package directories
    install_requires=[],  # Add dependencies if needed
    python_requires=">=3.12",  # Ensures compatibility with Python 3.12+
    description='A POS tagger for Pakistani English developed by Muhammad Owais',
    long_description=open('README.md').read(),  # Ensure README.md exists
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

