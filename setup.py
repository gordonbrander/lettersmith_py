from setuptools import setup, find_packages
from os import path

readme_path = path.join(path.dirname(__file__), "README.md")
with open(readme_path) as f:
    readme = f.read()

setup(
    name='lettersmith',
    version='0.0.1-alpha.1',
    author='Gordon Brander',
    description='Tools for static site generation',
    long_description=readme,
    license="MIT",
    url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "PyYAML>=3.13",
        "py-gfm>=0.1.3",
        "python-frontmatter>=0.3.1",
        "Jinja2>=2.7"
        # TODO
        # "watchdog>=0.6.0"
    ],
    extras_require={},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "lettersmith_scaffold=lettersmith.cli.scaffold:main",
        ]
    }
)
