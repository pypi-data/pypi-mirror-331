from setuptools import setup, find_packages

setup(
    name="pyperfcheck",
    version="0.1.0",
    packages=find_packages(where="pyprefcheck"),  # Ensures your package is found
    install_requires=[
        "psutil",
        "tabulate",
        "matplotlib",
        "asyncio"
    ],
    author="Janardhan Medathati",
    author_email="7janardhan7@gmail.com",
    description="A high-performance benchmarking library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Janardhan11/pyprefcheck",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
