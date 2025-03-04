from setuptools import setup, find_packages

setup(
    name="gepo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if needed
    entry_points={
        "console_scripts": [
            "gepo=gepo.gepo:main",
        ],
    },
    author="Baltej",
    author_email="baltej_s@outlook.com",
    description="gepo [GEtPOst] is a powerful, easy-to-use command-line tool for making HTTP requests. Built for developers, testers, and API enthusiasts.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/baltej223/gepo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

