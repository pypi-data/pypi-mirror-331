from setuptools import setup, find_packages


_ = setup(
    name="snapthing",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow==11.1.0",
        "PyAutoGUI==0.9.54",
    ],
    entry_points={
        "console_scripts": [
            "snapthing=snapthing.cli:main",
        ],
    },
    author="Blake Smith",
    author_email="blake@dotle.ca",
    description="A tool for taking screenshots",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://snap.dotle.ca",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

