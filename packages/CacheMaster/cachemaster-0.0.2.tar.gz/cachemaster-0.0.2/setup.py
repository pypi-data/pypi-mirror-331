from setuptools import setup, find_packages

setup(
    name="CacheMaster",
    version="0.0.2",
    description="A flexible caching system with in-memory and Redis support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jnardhan Singh",
    author_email="janardhansingh1998@gmail.com",
    url="https://github.com/JanardhanSingh98/CacheMaster",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["redis>=4.5.0"],
    extras_require={"dev": ["pytest>=7.0.0", "pytest-mock>=3.10"]},
    setup_requires=["setuptools>=65.0.0", "wheel>=0.40.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
