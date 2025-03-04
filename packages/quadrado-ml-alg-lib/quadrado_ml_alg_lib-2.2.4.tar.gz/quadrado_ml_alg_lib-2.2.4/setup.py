from setuptools import setup

setup(
    name='quadrado-ml-alg-lib',
    version='2.2.4',
    author='Quadrado',
    author_email='cheater22800000@gmail.com',
    packages=['maschine', 'programmador'],
    install_requires=[''], # TODO
    description='LIB FOR ML DEVs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/ваш_репозиторий',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
