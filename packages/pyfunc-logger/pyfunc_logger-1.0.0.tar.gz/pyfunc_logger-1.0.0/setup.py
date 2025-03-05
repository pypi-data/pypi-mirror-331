from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyfunc_logger",
    version="1.0.0",
    author="Yigal Weinberger",
    author_email="yigal.weinberger@gmail.com",
    description="Function call logging with precise timing for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yigal/pyfunc-logger",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
    keywords="logging, debugging, profiling, performance, function-calls",
)
