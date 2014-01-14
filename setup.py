from setuptools import setup


setup(
    name='piradio',
    version='0.1dev',
    entry_points={
        'console_scripts': [
            'piradio = piradio.manage:main'
        ]
    },
    test_suite='piradio.test',
    packages=['piradio'],
    package_data={'piradio': ['*.yaml']},
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    install_requires=[]
)
