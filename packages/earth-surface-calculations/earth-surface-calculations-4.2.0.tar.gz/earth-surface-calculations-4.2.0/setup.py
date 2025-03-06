from setuptools import setup, find_packages

setup(
    name="earth-surface-calculations",
    version="4.2.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["scipy", "numpy"],
    author="Hanry Zhang",
    author_email="popdoking@gmail.com",
    description="Geospatial utilities for Earth surface calculations",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suite="tests",
)
