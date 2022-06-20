from setuptools import setup, find_packages

setup(
    name='syncfail2ban',
    version='0.0.1.19062022',
    packages=find_packages(),
    package_dir={"": "src"},
    package_data={"src.data": ["config.cfg"]},
    py_modules=["syncfail2ban", ],
    entry_points={
        'console_scripts': [
            'syncfil2ban = syncfail2ban:main'
        ]
    },
    url='',
    license='Apache License 2.0',
    author='dominic porter',
    author_email='dominic.porter@dbpsolutions.com',
    description='sync fail2ban jails across servers & with OPNSense aliases'
)
