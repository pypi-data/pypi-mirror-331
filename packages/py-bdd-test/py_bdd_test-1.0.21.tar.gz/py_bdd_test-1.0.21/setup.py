from setuptools import setup, find_packages

setup(
    name="py-bdd-test",
    version='1.0.21',
    packages=find_packages(exclude=["bdd-test", "bdd-test.*"]),
    install_requires=[
        "behave",
        "kafka-python",
        "parse",
        "parse_type",
        "pyhamcrest",
        "requests",
        "PyHamcrest",
        "pyyaml",
        "python-multipart",
        "typing",
        "python-dotenv",
        "playwright",
        "kafka-python",
    ],
    entry_points={
        "console_scripts": [
            "list-bdd-steps=py_bdd_test.list_steps:main"
        ]
    },
    python_requires=">=3.7",
)
