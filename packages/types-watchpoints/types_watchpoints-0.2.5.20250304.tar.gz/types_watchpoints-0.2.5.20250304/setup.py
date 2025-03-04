from setuptools import setup

name = "types-watchpoints"
description = "Typing stubs for watchpoints"
long_description = '''
## Typing stubs for watchpoints

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`watchpoints`](https://github.com/gaogaotiantian/watchpoints) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `watchpoints`. This version of
`types-watchpoints` aims to provide accurate annotations for
`watchpoints==0.2.5`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/watchpoints`](https://github.com/python/typeshed/tree/main/stubs/watchpoints)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.395,
and pytype 2024.10.11.
It was generated from typeshed commit
[`a3a17b0f0e347b1ae769191a46e2e22168397b05`](https://github.com/python/typeshed/commit/a3a17b0f0e347b1ae769191a46e2e22168397b05).
'''.lstrip()

setup(name=name,
      version="0.2.5.20250304",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/watchpoints.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['watchpoints-stubs'],
      package_data={'watchpoints-stubs': ['__init__.pyi', 'ast_monkey.pyi', 'util.pyi', 'watch.pyi', 'watch_element.pyi', 'watch_print.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
