import os
from pathlib import Path
from setuptools import setup

def read(file_name):
    with open(
        os.path.join(
            Path(os.path.dirname(__file__)),
            file_name)
    ) as _file:
        return _file.read()


long_description = read('README.md')


setup(
    name='custom_deferrable_dataflow_operator',
    version='1.0.0',
    description="Start your Dataflow jobs execution directly from the Triggerer without going to the Worker.",
    url='https://github.com/AlvaroCavalcante/airflow-custom-deferrable-dataflow-operator',
    download_url='https://github.com/AlvaroCavalcante/airflow-custom-deferrable-dataflow-operator',
    license='Apache License 2.0',
    author='Alvaro Leandro Cavalcante Carneiro',
    author_email='alvaroleandro250@gmail.com',

    py_modules=['__init__', 'dataflow_trigger',
                'deferrable_dataflow_operator'],
    package_dir={'': 'src'},

    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=[
        'airflow',
        'apache-airflow',
        'python',
        'python3',
        'dataflow',
        'gcp',
        'cloud-composer',
        'google-cloud',
        'dag',
        'benchmark',
        'apache',
        'data',
        'data-engineering'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Apache Airflow',
    ],
    python_requires='>=3.8',
    install_requires=[
        'apache-airflow>=2.10.0',
        'google-cloud>=0.33.0',
    ]
)
