from setuptools import setup, find_namespace_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='opengenome',
    version='0.1.2',
    long_description=description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(where="src"),
    package_dir={'': 'src'},
    install_requires=[],
    include_package_data=True,
    package_data={"": ["*.yaml"]},
    entry_points={
        "console_scripts": [
            "opengenome-about = opengenome:about",
        ],
    },
    extras_require={
        "dev": [
            "mypy",
            "pytest",
            "pytest-cov",
            "jupyter",
            "sphinx",
            "myst-nb",
            "sphinx-autoapi",
            "pydata_sphinx_theme",
        ]
    },
)
