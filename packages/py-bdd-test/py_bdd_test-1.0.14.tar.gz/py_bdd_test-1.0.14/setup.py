from setuptools import setup, find_packages

setup(
    name="py-bdd-test",
    version="1.0.14",
    packages=find_packages(),  # Automatically finds "py_bdd_test"
    install_requires=[
        "behave",
        "kafka-python",
        "parse",
        "parse_type",
        "pyhamcrest",
        "behavex",
        "requests",
        "PyHamcrest",
        "pyyaml",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pymongo",
        "pydantic",
        "typing",
        "python-dotenv",
        "playwright",
        "kafka-python",
    ],
    python_requires=">=3.7",
)
