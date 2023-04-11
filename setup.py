from setuptools import setup


setup(
    name="gdtoolkit",
    version="4.0.1",
    description="Independent set of tools for working with GDScript - parser, linter and formatter",
    keywords=["GODOT", "GDSCRIPT", "PARSER", "LINTER", "FORMATTER"],
    url="https://github.com/Scony/godot-gdscript-toolkit",
    author="Pawel Lampe",
    author_email="pawel.lampe@gmail.com",
    license="MIT",
    packages=[
        "gdtoolkit",
        "gdtoolkit.linter",
        "gdtoolkit.formatter",
        "gdtoolkit.parser",
        "gdtoolkit.common",
        "gdtoolkit.gd2py",
        "gdtoolkit.gdradon",
    ],
    package_data={"gdtoolkit.parser": ["gdscript.lark", "comments.lark"]},
    entry_points={
        "console_scripts": [
            "gdparse = gdtoolkit.parser.__main__:main",
            "gdlint = gdtoolkit.linter.__main__:main",
            "gdformat = gdtoolkit.formatter.__main__:main",
            "gd2py = gdtoolkit.gd2py.__main__:main",
            "gdradon = gdtoolkit.gdradon.__main__:main",
        ]
    },
    include_package_data=True,
    install_requires=[
        "lark[regex]==1.1.5",
        "docopt-ng==0.8.1",
        "pyyaml>=5.1",
        "radon==6.0.1",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
