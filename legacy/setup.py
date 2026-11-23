from setuptools import setup, find_packages

setup(
    name="aegis_grid",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pycryptodome>=3.10.1",
    ],
    author="Burhan Abdullah",
    description="Proprietary Agentic Cryptographic Framework for Grid Security",
    python_requires=">=3.10",
)
