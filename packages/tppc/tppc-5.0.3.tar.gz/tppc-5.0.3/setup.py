from setuptools import setup, find_packages

setup(
    name="tppc",
    version="5.0.3",
    author="Sean Tichenor",
    description="T++ Quantum Execution Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_GITHUB_USERNAME/tppc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": [
            "tppc=tppc.__main__:main",
        ],
    },
    install_requires=["pyyaml"],
)
