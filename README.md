# `CMakePythonDeps` Generator

This is a conan `python_requires` package, exposing functionality to generate CMake targets for executables in a python virtual environment.

For a recipe to be consumed using the `CMakePythonDeps` generator, populate the `self.user_info.python_requirements` and `self.user_info.python_env` `package_info()` variables as below:

```python
class PythonVirtualEnvironment(ConanFile):

    def package_info(self):
        requirements = [
            "sphinx==4.4.0",
            "sphinx_rtd_theme",
            "sphinx_book_theme==0.3.2",
            "pygments",
        ]
        self.user_info.python_requirements = json.dumps(requirements)
        self.user_info.python_envdir = self.package_folder
```

* `user_info.python_requirements`: This is expected to be a JSON string containing a list of the packages and their versions to be installed into the virtual environment.
* `user_info.python_envdir`: A string representing the path to the python virtual environment.

An example of a package that uses this is the [`python-virtualenv/system`](https://github.com/samuel-emrys/python-virtualenv) package.

To consume a recipe that has populated the above variables, simply specify `CMakePythonDeps` as the generator to use in the consumer `conanfile.py`:

```python
class ExamplePythonConan(ConanFile):
    # ...
    python_requires = "CMakePythonDeps/0.1.0"

    def generate(self):
        py = python_requires["CMakePythonDeps"].modules.CMakePythonDeps(self)
        py.generate()
```

This generator will create CMake targets named for the package, and it's executables to allow you to use them in your CMake recipes. To illustrate, if you were to install `sphinx` in a virtual environment, the entry points `sphinx-build`, `sphinx-quickstart`, `sphinx-apidoc` and `sphinx-autogen` would be created in the virtual environment. The corresponding CMake targets would be:

```cmake
sphinx::sphinx-build
sphinx::sphinx-quickstart
sphinx::sphinx-apidoc
sphinx::sphinx-autogen
```

This means that a minimal `docs/CMakeLists.txt` for a sphinx dependency might look like the following:

```cmake
find_package(sphinx REQUIRED)

# Sphinx configuration
set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR})
set(SPHINX_BUILD ${CMAKE_CURRENT_BINARY_DIR}/sphinx)
set(SPHINX_INDEX_FILE ${SPHINX_BUILD}/index.html)

# Only regenerate Sphinx when:
# - Doxygen has rerun
# - Our doc files have been updated
# - The Sphinx config has been updated
add_custom_command(
  OUTPUT ${SPHINX_INDEX_FILE}
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/index.rst
  COMMAND sphinx::sphinx-build -b html ${SPHINX_SOURCE} ${SPHINX_BUILD}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Generating documentation with Sphinx")

add_custom_target(sphinx ALL DEPENDS ${SPHINX_INDEX_FILE})

# Add an install target to install the docs
include(GNUInstallDirs)
install(DIRECTORY ${SPHINX_BUILD}/ DESTINATION ${CMAKE_INSTALL_DOCDIR})

```

An example of this being used in conjunction with `python-virtualenv` is [`sphinx-consumer`](https://github.com/samuel-emrys/sphinx-consumer).

