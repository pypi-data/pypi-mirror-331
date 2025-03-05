from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='netsuite_python',
    version='2.1.1',
    description='Python SDK for Netsuite API with Flask Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/codinlikewilly/netsuite_python',
    readme="README.md",
    author='Will @ TheAPIGuys',
    author_email='will@theapiguys.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'PyJWT',
        "urllib3 >= 1.15",
        "six >= 1.10",
        "certifi",
        "python-dateutil",
        "pyOpenSSL",
        "cryptography",
    ],
    entry_points={
        'console_scripts': [
            'netsuite = netsuite.scripts.cli:cli',
        ],

    },
)
