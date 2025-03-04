from setuptools import setup, find_packages

setup(
    name='digitalocean_access_spaces',
    version='1.2',
    packages=find_packages(),
    install_requires=[
        'boto3==1.35.99',
    ],
    url='https://github.com/lupin-oomura/digitalocean_access_spaces.git',
    author='Shin Oomura',
    author_email='shin.oomura@gmail.com',
    description='',
)
