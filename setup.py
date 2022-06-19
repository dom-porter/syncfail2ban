from setuptools import setup, find_packages

setup(
    name='syncfail2ban',
    version='0.0.1.19062022',
    packages=find_packages(),
    package_dir={"": "src"},
    package_data={"src.data": ["config.cfg"]},
    url='',
    license='Apache License 2.0',
    author='dominic porter',
    author_email='dominic.porter@dbpsolutions.com',
    description='sync fail2ban jails across servers & with OPNSense aliases'
)
