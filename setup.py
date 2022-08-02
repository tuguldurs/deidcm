from setuptools import setup

setup(
    name='deidcm',
    version='0.0.1',
    packages=['deidcm'],
    install_requires=[
        'tqdm>=4.62',
        'pydicom==2.3.0'
    ],
    python_requires='>=3.9',
)
