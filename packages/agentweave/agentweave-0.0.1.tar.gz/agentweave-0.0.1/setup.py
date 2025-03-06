"""Setup script for AgentWeave."""

from setuptools import find_packages, setup

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Read long description
with open("README.md") as f:
    long_description = f.read()

setup(
    name="agentweave",
    version="0.0.1",
    description="A scalable and accessible framework for building AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AgentWeave Team",
    author_email="info@agentweave.io",
    url="https://github.com/AgentWeave/agentweave",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "agentweave=agentweave.cli.main:main",
        ],
    },
)
