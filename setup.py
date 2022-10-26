from setuptools import setup

setup(
    name='deidcm',
    version='0.0.1',
    packages=['deidcm'],
    install_requires=[
        'tqdm>=4.62',
        'pydicom==2.3.0',
        'boto3>=1.24'
    ],
    python_requires='>=3.7.10',
)
