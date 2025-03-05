from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

"""Perform the package airflow-provider-demo-ml-framework setup."""
setup(
    name='airflow-provider-demo-ml-framework',
    version="0.1.4",
    description='demo-ml-framework airflow provider.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        "apache_airflow_provider": ["provider_info=ml_demo_provider.__init__:get_provider_info"]
    },
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: Other/Proprietary License",
    ],
    packages=[
        'ml_demo_provider',
        'ml_demo_provider.hooks',
        'ml_demo_provider.sensors',
        'ml_demo_provider.operators',
        'ml_demo_provider.operators.ml',
    ],
    install_requires=['apache-airflow>=2.3.0'],
    setup_requires=['setuptools', 'wheel'],
    author='osaienko',
    author_email='alsaienko81@gmail.com',
    url='https://www.trendscape.ai/',
    python_requires='~=3.7',
)
