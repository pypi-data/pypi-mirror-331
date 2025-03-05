from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='rcon_host',
    version='0.1',
    author='local1ka',
    author_email='alexarst@mail.ru',
    description='The RCON-Host library allows you to accept user commands using the RCON protocol.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/local1ka/rcon-host.git',
    packages=find_packages(),
    keywords='rcon rcon_host rcon-host rcon_server rcon-server local1ka ',
    project_urls={
        'GitHub': 'https://github.com/local1ka/rcon-host.git'
    },
    python_requires='>=3.6'
)
