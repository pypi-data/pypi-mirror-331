"""Databricks GenAI package"""

from setuptools import find_packages, setup

# pylint: disable-next=exec-used,consider-using-with
exec(open('databricks/model_training/version.py', 'r', encoding='utf-8').read())

install_requires = [
    'backoff>=2.2.1',
    'databricks-sdk>=0.29.0,<=0.44.1',
    'datasets>=2.16.1,<=3.3.2',
    'gql[websockets]>=3.4.0',
    'mlflow>=2.14.2,<=2.20.2',
    'mosaicml-cli>=0.6',
    'requests>=2.26.0,<3',
    'boto3>=1.36,<2',
    'typing_extensions>=4.7.1',
    'pydantic>=2',
    'databricks-agents==0.16.0',
    'tenacity>=9.0.0',
    'rich>=12.6.0',
    'openai>=1.56,<2',
    'rouge-score>=0.1.2',
    'evaluate>=0.4.3',
    'catalogue>=2.0.10,<3',
    'IPython>=8,<9',
    'freezegun>=1.5,<2',
]

extra_deps = {}

extra_deps['spark'] = [
    'databricks-connect==16.0.0',
]

extra_deps['dev'] = [
    'isort>=5.9.3',
    'packaging>=21,<25',
    'parameterized==0.9',
    'pre-commit>=2.17.0',
    'pylint>=3.0.0',
    'pyright==1.1.256',
    'pytest>=7.4.0',
    'yapf>=0.40.0',
]

extra_deps['release'] = [
    'build>=0.10.0',
    'twine>=4.0.2',
]

extra_deps['notebook'] = ['ipywidgets>=8,<9']

extra_deps['all'] = set(dep for deps in extra_deps.values() for dep in deps)

setup(
    name='databricks-genai',
    version=__version__,  # type: ignore pylint: disable=undefined-variable
    author='Databricks',
    author_email='genai-eng-team@databricks.com',
    description='Interact with the Databricks Generative AI APIs in python',
    url='https://docs.mosaicml.com/projects/mcli/en/latest/finetuning/finetuning.html',  # TODO: update with DBX docs
    include_package_data=True,
    package_data={},
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=install_requires,
    extras_require=extra_deps,
    python_requires='>=3.10',
    ext_package='databricks_genai',
)
