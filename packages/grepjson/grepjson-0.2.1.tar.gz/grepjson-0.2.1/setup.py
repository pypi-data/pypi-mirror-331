from setuptools import setup

setup(
    name="grepjson",
    version="0.2.1",
    py_modules=["grepjson"],
    install_requires=[],  
    entry_points={
        'console_scripts': [
            'grepjson = grepjson:main',
        ],
    },
    author="Juhayna",
    author_email="juhayna@foxmail.com",
    description="Interactively inspect or process JSON/JSONL data from pipe.",
    keywords="json debug cli",
    url="https://github.com/juhayna-zh/grepjson",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)