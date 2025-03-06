from setuptools import setup, find_packages

setup(
    name="py-bdd-test",
    version="1.0.12",
    packages=find_packages(include=["py_bdd_test", "py_bdd_test.*"]),  # Ensure submodules are found
    include_package_data=True,  # Needed for non-Python files
    package_data={
        "py_bdd_test": ["features/steps/*.py", "features/*.feature"],
    },
    install_requires=[
        "behave",
        "parse",
        "parse_type",
        "kafka-python",
        "pyhamcrest",
    ],
)
