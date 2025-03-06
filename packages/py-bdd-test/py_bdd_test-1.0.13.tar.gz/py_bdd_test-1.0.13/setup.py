from setuptools import setup, find_packages

setup(
    name="py-bdd-test",
    version="1.0.13",
    packages=find_packages(),  # Automatically finds "py_bdd_test"
    install_requires=[
        "behave",
        "kafka-python",
        "parse",
        "parse_type",
        "pyhamcrest"
    ],
    python_requires=">=3.7",
)
