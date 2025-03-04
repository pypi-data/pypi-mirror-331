from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="py-ethiopian-date-converter",
    version="0.1.1",  # Update this for new releases
    author="Birhanu Gudisa",
    author_email="bir13gud17@gmail.com",
    description="A Python package to convert dates between Gregorian and Ethiopian calendars.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GutemaG/py_ethiopain_date_converter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],  # Add dependencies here if any
)
