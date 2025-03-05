import os
from setuptools import setup, find_packages

requirements = ''

requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path) as f:
        requirements = f.read().splitlines()
        
print(requirements)

if __name__ == '__main__':
    setup(
        name="eyeloc",
        version="0.1.2",
        packages=find_packages(),
        install_requires=requirements,
        author="Maxim Proshkin",
        author_email="max.proshkin@mail.ru",
        description="Python package for localization tasks on eye images",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        url="https://github.com/promaxV/eyeloc",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.8',
    )
