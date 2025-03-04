from setuptools import setup, find_packages

setup(
    name="NXDB",
    version="0.1.0.7",
    packages=find_packages(),
    install_requires=["pyyaml"],
    entry_points={
        "console_scripts": [
            'nxdb-cli = nxdb.cli:main'
        ]
    },
    author="VladosNX",
    author_email="email.name@email.com"
)

# Run `python3 setup.py sdist bdist_wheel`
