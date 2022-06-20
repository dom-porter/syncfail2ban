from setuptools import setup, find_packages

setup(
    name='syncfail2ban',
    version='0.0.1.19062022',
    packages=find_packages(include=['src.syncfail2ban', 'src.syncfail2ban.*']),
    package_dir={"syncfail2ban": "src"},
    package_data={"src.data": ["config.cfg"]},
    py_modules=["syncfail2ban",
                "AliasController",
                "Firewall",
                "OpnSense",
                "SyncConfig",
                "SyncOPNThread",
                "UpdateThread", ],
    entry_points={
        'console_scripts': [
            'syncfail2ban = syncfail2ban:main',
        ]
    },
    install_requires=['pyzmq~=22.3.0',
                      'requests~=2.25.1',
                      'configparser~=5.2.0'],
    url='',
    license='Apache License 2.0',
    author='dominic porter',
    author_email='dominic.porter@dbpsolutions.com',
    description='sync fail2ban jails across servers & with OPNSense aliases'
)
