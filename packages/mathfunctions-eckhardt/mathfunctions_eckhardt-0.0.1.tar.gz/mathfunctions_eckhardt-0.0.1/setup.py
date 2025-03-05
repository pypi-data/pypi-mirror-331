from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='mathfunctions-eckhardt',
    version='0.0.1',
    license='MIT License',
    author='Guilherme Eckhardt',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='eckhardt.gui@gmail.com',
    keywords='multmat',
    description=u'Um repositório para fins acadêmicos',
    packages=['eckhardt'],)