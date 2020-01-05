from setuptools import setup


setup(
    name="gdtoolkit",
    version="0.3",
    description="Independent, standalone set of tools for working with GDScript",
    url="https://github.com/Scony/godot-gdscript-toolkit",
    author="Pawel Lampe",
    author_email="pawel.lampe@gmail.com",
    license="MIT",
    packages=[
        "gdtoolkit",
        "gdtoolkit.linter",
        "gdtoolkit.formatter",
        "gdtoolkit.parser",
    ],
    package_data={"gdtoolkit.parser": ["gdscript.lark"]},
    entry_points={
        "console_scripts": [
            "gdparse = gdtoolkit.parser.__main__:main",
            "gdlint = gdtoolkit.linter.__main__:main",
        ]
    },
    include_package_data=True,
    install_requires=["lark-parser>=0.7.8", "docopt>=0.6.2", "pyyaml>=5.1",],
    python_requires=">=3",
)
