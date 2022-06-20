from setuptools import setup, find_packages

setup(
    name='syncfail2ban',
    version='0.0.1.19062022',
    packages=find_packages(),
    package_dir={"": "src"},
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
            'syncfail2ban = syncfail2ban:main'
        ]
    },
    install_requires=['zmq'],
    url='',
    license='Apache License 2.0',
    author='dominic porter',
    author_email='dominic.porter@dbpsolutions.com',
    description='sync fail2ban jails across servers & with OPNSense aliases'
)
