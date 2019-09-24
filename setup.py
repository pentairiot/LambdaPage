from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='LambdaPage',
    version='0.0.11',
    author='PentairIoT',
    author_email='pentairiot@gmail.com',
    description='Python library for creating, testing, and deploying small single-page web applications using AWS Lambda and API-Gateway',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pentairiot/LambdaPage',
    packages=["LambdaPage"],
    install_requires=["pytz"],
    extras_require={"aws": ["boto3"], "local": ["falcon"]},
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
