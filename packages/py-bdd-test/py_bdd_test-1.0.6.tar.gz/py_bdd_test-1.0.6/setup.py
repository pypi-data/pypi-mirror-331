from setuptools import setup, find_packages

setup(
    name="py-bdd-test",
    version="1.0.6",
    packages=find_packages(include=["py_bdd_test", "py_bdd_test.*"]),
    package_data={
        "py_bdd_test": ["features/steps/*.py"],
    },
    include_package_data=True,
    install_requires=[
        "behave",
        "parse",
        "parse_type",
        "kafka-python",
        "pyhamcrest",
    ],
)
