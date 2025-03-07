from setuptools import setup, find_packages

setup(
    name='DynamiSpectra',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Adicione bibliotecas necessárias, como:
        'numpy',
        'matplotlib',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'dynami=dynamiSpectra.main:main',  # Ajuste conforme o ponto de entrada
        ],
    },
    author='Iverson Conrado-Bezerra',
    author_email='iverson.coonrado@gmail.com',
    description='Molecular dynamics scripts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SeuUsuario/DynamiSpectra',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
