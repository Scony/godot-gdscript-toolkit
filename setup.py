from setuptools import setup


setup(
    name='gdtoolkit',
    version='0.1',
    description='Independent, standalone set of tools for working with GDScript',
    url='https://github.com/Scony/godot-gdscript-toolkit',
    author='Pawel Lampe',
    author_email='pawel.lampe@gmail.com',
    license='MIT',
    packages=['gdtoolkit'],
    package_data={
        'gdtoolkit': ['gdscript.lark']
    },
    scripts=[
        'bin/gdparse',
        'bin/gdlint',
    ],
    include_package_data=True,
    install_requires=[
        'lark-parser>=0.7.8',
        'docopt>=0.6.2',
        'pyyaml>=5.1',
    ],
    python_requires='>=3'
)
