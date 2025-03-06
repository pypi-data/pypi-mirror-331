import os
import re
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

def read_version(package_name):
    package_path = os.path.join(package_name, '__init__.py')
    with open(package_path, 'r', encoding='utf-8') as f:
        version_file = f.read()

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

PACKAGE_NAME = 'upyboard'

setup(
    name=PACKAGE_NAME,
    version=read_version(PACKAGE_NAME),
    description='This is a CLI tool for MicroPython-based embedded systems.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='chanmin.park',
    author_email='devcamp@gmail.com',
    url='https://github.com/planxstudio/upyboard',
    install_requires=['click', 'python-dotenv', 'pyserial', 'genlib', 'mpy-cross'],
    packages=find_packages(),
    keywords=['micropython', 'pyserial', 'genlib'],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'upy = upyboard.upy:main',    
        ],
    },
)
