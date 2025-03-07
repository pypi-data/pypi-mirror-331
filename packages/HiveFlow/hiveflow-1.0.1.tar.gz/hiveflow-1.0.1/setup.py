from setuptools import setup, find_packages

# Read README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from file
with open("src/hiveflow/version.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"

setup(
    name="HiveFlow",
    version=version,
    author="changyy",
    author_email="changyy.csie@gmail.com",
    description="A scalable, distributed producer/consumer framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/changyy/py-HiveFlow",
    project_urls={
        "Bug Tracker": "https://github.com/changyy/py-HiveFlow/issues",
        "Documentation": "https://py-hiveflow.readthedocs.io",
        "Source Code": "https://github.com/changyy/py-HiveFlow",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "redis>=5.0.0",
        "asyncpg>=0.28.0",
        "sqlalchemy>=2.0.22",
        "pydantic>=2.4.2",
        "aiohttp>=3.8.6",
        "click>=8.1.7",
        "jinja2>=3.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "isort>=5.12.0",
            "mypy>=1.6.1",
            "flake8>=6.1.0",
            "pre-commit>=3.5.0",
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hiveflow=hiveflow.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hiveflow": ["templates/*", "templates/*.template"],
    },
)
