"""Setup configuration for wikipedia-terminal."""
from setuptools import setup, find_packages

def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Offline Wikipedia reader for the terminal"

def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["zimply>=1.1.0", "prompt-toolkit>=3.0.0"]

setup(
    name="wikipedia-terminal",
    version="0.1.0",
    author="Rafael Chandane",
    description="Offline Wikipedia reader for the terminal with Fallout-style interface",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/rafaelchandane/wikipedia-terminal",
    project_urls={
        "Bug Tracker": "https://github.com/rafaelchandane/wikipedia-terminal/issues",
        "Documentation": "https://github.com/rafaelchandane/wikipedia-terminal#readme",
        "Source Code": "https://github.com/rafaelchandane/wikipedia-terminal",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "wiki-term=wikipedia_tui.ui_curses:main",
        ],
    },
    keywords="wikipedia offline terminal cli zim kiwix",
    include_package_data=True,
    zip_safe=False,
)
