from setuptools import setup
from pip.req import parse_requirements

print([str(r.req).split('==')[0] for r in parse_requirements('requirements.txt')])

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
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    install_requires=[]
)
