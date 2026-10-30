"""The one place ASSAY's version is written.

pyproject.toml reads it from here (``[tool.setuptools.dynamic]``), the package
re-exports it as ``assay_production.__version__``, and both command-line
tools print it for ``--version``. ``tests/test_packaging.py`` checks that
these, the installed metadata and the top entry of CHANGELOG.md all agree.
"""
__version__ = "0.11.9"
