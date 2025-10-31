from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="usecasesimulator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    author="Shad Safa",
    author_email="shad.safa@example.com",
    description="A comprehensive business simulation game for learning strategic decision making",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShadSafa/UseCaseSimulator",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    keywords="business simulation game education strategy decision-making",
    project_urls={
        "Homepage": "https://github.com/ShadSafa/UseCaseSimulator",
        "Repository": "https://github.com/ShadSafa/UseCaseSimulator",
        "Issues": "https://github.com/ShadSafa/UseCaseSimulator/issues",
        "Documentation": "https://github.com/ShadSafa/UseCaseSimulator/blob/main/docs/",
        "Changelog": "https://github.com/ShadSafa/UseCaseSimulator/blob/main/CHANGELOG.md",
    },
)
