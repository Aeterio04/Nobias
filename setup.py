"""
NoBias - Comprehensive Bias Detection and Mitigation Library
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')

setup(
    name="unbiased",
    version="0.0.0",
    author="NoBias Team",
    author_email="contact@nobias.dev",
    description="Comprehensive bias detection and mitigation for datasets, models, and LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nobias/unbiased",
    project_urls={
        "Bug Tracker": "https://github.com/nobias/unbiased/issues",
        "Documentation": "https://github.com/nobias/unbiased/blob/main/docs",
        "Source Code": "https://github.com/nobias/unbiased",
    },
    package_dir={"": "library"},
    packages=find_packages(where="library"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "agent": [
            "groq>=0.4.0",
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "aiohttp>=3.9.0",
        ],
        "reports": [
            "reportlab>=4.0.0",
            "matplotlib>=3.7.0",
        ],
        "embeddings": [
            "sentence-transformers>=2.2.0",
        ],
        "langgraph": [
            "langgraph>=0.2.0",
            "langchain>=0.3.0",
            "langchain-groq>=0.2.0",
        ],
        "server": [
            "fastapi>=0.115.0",
            "uvicorn>=0.32.0",
        ],
        "all": [
            "groq>=0.4.0",
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "aiohttp>=3.9.0",
            "reportlab>=4.0.0",
            "matplotlib>=3.7.0",
            "sentence-transformers>=2.2.0",
            "langgraph>=0.2.0",
            "langchain>=0.3.0",
            "langchain-groq>=0.2.0",
            "fastapi>=0.115.0",
            "uvicorn>=0.32.0",
        ],
    },
    include_package_data=True,
    package_data={
        "unbiased": ["py.typed"],
        "unbiased.agent_audit.personas": ["data/*.json"],
    },
    keywords=[
        "bias",
        "fairness",
        "machine-learning",
        "ai",
        "llm",
        "audit",
        "ethics",
        "responsible-ai",
        "dataset-audit",
        "model-audit",
        "agent-audit",
    ],
    zip_safe=False,
)
