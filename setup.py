import os
from setuptools import setup


setup(
    name='jira-time-logger',
    use_scm_version=True,
    author='Vasily Kuznetsov',
    author_email='kvas.it@gmail.com',
    maintainer='Vasily Kuznetsov',
    maintainer_email='kvas.it@gmail.com',
    license='MIT',
    url='https://github.com/kvas-it/jira-time-logger',
    description='Command line tool to log time in Jira',
    py_modules=['jira_time_logger'],
    install_requires=['jira', 'keyring'],
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': [
            'jtl = jira_time_logger:main',
        ],
    },
)

