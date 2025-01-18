from setuptools import setup, find_packages

setup(
    name="dida365",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
        "python-dotenv>=1.0.0",
        "tomli>=2.0.0",
        "pydantic-settings>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
) 