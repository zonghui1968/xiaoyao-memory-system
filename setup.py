"""Setup script for xiaoyao-memory-system."""

from setuptools import setup, find_packages
from pathlib import Path

readme = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

requirements = [
    "networkx>=3.0",
    "pydantic>=2.0",
    "numpy>=1.24.0",
    "lancedb>=0.5.0",
    "aiohttp>=3.8.0",
    "requests>=2.28.0",
]

extras_require = {
    "embeddings": ["sentence-transformers>=2.2.0"],
    "web": ["flask>=3.0.0", "flask-cors>=4.0.0"],
    "test": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    "all": [
        "sentence-transformers>=2.2.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
}

setup(
    name="xiaoyao-memory-system",
    version="9.5.0",
    author="Zonghui Yang (小妖🦊)",
    author_email="hizonghui@gmail.com",
    description="AI记忆系统 - 基于MemPalace的记忆宫殿架构",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/zonghui1968/xiaoyao-memory-system",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "xiaoyao-memory=xiaoyao_memory_system.cli:main",
        ],
    },
)
