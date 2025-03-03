from setuptools import setup, find_packages

setup(
    name="root-vortex",
    version="2.1.5",
    author="Sean Tichenor",
    description="Quantum AI Secure Root Execution",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_GITHUB_USERNAME/root-vortex",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": [
            "root-vortex=root_vortex.__main__:main",
        ],
    },
    install_requires=[],
)
