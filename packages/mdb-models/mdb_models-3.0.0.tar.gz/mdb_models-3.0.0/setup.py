from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'mdb_models/README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='mdb-models',
    description='A data mapper for mongodb (Formerly mongodb_data_layer)',
    version='3.0.0',
    packages=find_packages(include=['mdb_models', 'mdb_models.*']),
    install_requires=[
        'pymongo',
        'python-dotenv',
        'bcrypt'
    ],
    author="Marjon Godito",
    entry_points={
        'console_scripts': [
            'generate-model=mdb_models.generate_model:main',
            'generate-authmodel=mdb_models.generate_authmodel:main'
        ]
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
)