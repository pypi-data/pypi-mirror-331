from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='rcon_fake',
    version='0.1',
    author='local1ka',
    author_email='alexarst@mail.ru',
    description='The RCON-Fake library allows you to accept user commands using the RCON protocol.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/local1ka/rcon-fake.git',
    packages=find_packages(),
    project_urls={
        'GitHub': 'https://github.com/local1ka/rcon-fake.git'
    },
    python_requires='>=3.6'
)
