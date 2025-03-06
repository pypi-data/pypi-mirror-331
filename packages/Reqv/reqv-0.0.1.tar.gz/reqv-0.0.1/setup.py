from setuptools import setup, find_packages

setup(
    name="Reqv", 
    version="0.0.1", 
    packages=find_packages(), 
    install_requires=[  # Dependencies
        "httpx", "requests"
    ],
    description="A Python library for scraping data from APIs in modern websites.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Vishva Allen",  
    author_email="jvishvateja26@gmail.com", 
    license="MIT",  
    classifiers=[ 
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
