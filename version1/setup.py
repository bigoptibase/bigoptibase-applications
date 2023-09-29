"""setup.py file"""
import uuid

from setuptools import setup, find_packages

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]

# script_dir = 'scripts'
# scripts = [
#     'script_template',
# ]
#
# scripts = ['{0}/{1}'.format(script_dir, script) for script in scripts]

setup(
    name="dcss",
    version="0.2.6",
    packages=find_packages(),
    # package_data={'smworker.resources': ['templates/*', 'logos/*', 'examples/*']},
    # scripts=scripts,
    author="Adam Pavlidis",
    author_email="apavlidis@netmode.ntua.gr",
    description="Data Collection Scheduling System",
    install_requires=reqs
)
