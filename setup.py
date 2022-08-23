from setuptools import setup

setup(
    name='deidcm',
    version='0.0.1',
    packages=['deidcm'],
    install_requires=[
        'tqdm>=4.62',
        'pydicom==2.3.0',
        'pyinstaller>=4.8',
        'gooey>=1.0.8',
        'names==0.3.0'
    ],
    python_requires='>=3.9',
)
