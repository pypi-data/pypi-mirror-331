from setuptools import setup, find_packages

setup(
    name="agentstable",
    version="0.1.0",
    description="SDK for interacting with tool discovery service and agents.json files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Clayton D'Cruze",
    author_email="claytondcruze@example.com",
    url="https://github.com/claytondcruze/agentstable-sdk",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.0.0",
        "jsonschema>=4.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="agents, tools, discovery, llm, claude, openai",
    python_requires=">=3.8",
)
