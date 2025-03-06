from setuptools import setup, find_packages
from pathlib import Path

def find_scripts():
    scripts = []
    for script in Path('scripts').iterdir():
        if script.is_file():
            scripts.append(str(script))
    return scripts

def find_deps():
    with open('requirements.txt') as f:
        return [l.strip() for l in f.read().splitlines() if len(l.strip()) > 0]

scripts = find_scripts()

setup(
    name='pycloudshare',
    version='1.0',
    packages=find_packages(),
    install_requires=find_deps(),
    author="Daniel S. Robbins",
    author_email="daniel.robbins@alabama-cyber-range.org",
    description="A Python wrapper for the CloudShare Classic and Accelerate APIs",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/MerakiLoogie',
    scripts=find_scripts(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
