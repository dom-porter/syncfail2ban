from setuptools import setup, find_packages

setup(
    name='syncfail2ban',
    version='0.0.1.20062022',
    packages=find_packages(),
    pymodules =['syncfail2ban', 'syncfail2ban_client', ],
    entry_points={
        'console_scripts': ["syncfail2ban = syncfail2ban:main",
                            "syncfail2ban_client = syncfail2ban_client:main"],
    },
    install_requires=['pyzmq~=22.3.0',
                      'requests~=2.25.1',
                      'configparser~=5.2.0'],
    url='',
    license='Apache License 2.0',
    author='Dominic Porter',
    author_email='open.source@dbpsolutions.com',
    description='sync fail2ban jails across servers & with OPNSense aliases'
)
