from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import save

import json
import sys
import os
import textwrap

from pathlib import Path


class CMakePythonDepsConan(ConanFile):
    name = "CMakePythonDeps"
    version = "0.2.1"

    # Optional metadata
    url = "https://github.com/samuel-emrys/cmake-python-deps.git"
    homepage = "https://github.com/samuel-emrys/cmake-python-deps.git"
    license = "MIT"
    description = "A python_requires library providing a CMake generator to expose executables in python virtual environments as CMake targets"
    topics = ("Python", "Virtual Environment", "CMake", "venv")
    no_copy_source = True

    python_requires = "pyvenv/0.1.0@mtolympus/stable"

    def init(self):
        CMakePythonDeps.venv = self.python_requires["pyvenv"].module.PythonVirtualEnv


class CMakePythonDeps(object):
    venv = None

    def __init__(self, conanfile):
        self._conanfile = conanfile

    @property
    def binpath(self):
        return "Scripts" if self._conanfile.settings.os == "Windows" else "bin"

    @property
    def ext(self):
        return ".exe" if self._conanfile.settings.os == "Windows" else ""

    @property
    def content(self):
        config = {}
        for dep_name, dependency in self._conanfile.dependencies.items():
            package_targets = {}
            # Add targets for python and pip
            package_targets["python"] = ["python", "pip"]

            requirements = {}
            python_envdir = dependency.conf_info.get("user.env.pythonenv:dir")
            requirements_conf = dependency.conf_info.get('user.env.pythonenv:requirements')
            if requirements_conf:
                requirements = json.loads(requirements_conf)

            # If the generator has been provided with a virtual environment to scan
            if python_envdir:
                path = Path(python_envdir, self.binpath, f"python{self.ext}")
                realname = path.resolve(strict=True).name
                interpreter = str(path.with_name(realname))
                virtualenv = self.venv(
                    self._conanfile,
                    python=interpreter,
                    env_folder=python_envdir,
                )

                for requirement in requirements:
                    package = requirement.split("==")[0]
                    entry_points = virtualenv.entry_points(package)
                    package_targets[package] = entry_points.get("console_scripts", [])

                for package, targets in package_targets.items():
                    for target in targets:
                        exe_path = None
                        for path_ in [
                            Path(self.binpath, f"{target}{self.ext}"),
                            Path("lib", f"{target}{self.ext}"),
                        ]:
                            if Path(python_envdir, path_).is_file():
                                exe_path = Path(python_envdir, path_)
                                break
                        if not exe_path:
                            raise ConanException(f"Could not find path to {target}{self.ext}")
                        else:
                            exe_path_str = (
                                str(exe_path)
                                if sys.platform != "win32"
                                else str(exe_path).replace("\\", r"\\")
                            )
                            filename = f"{package}-config.cmake"
                            config[filename] = config.get(filename, "") + textwrap.dedent(
                                f"""\
                                if(NOT TARGET {package}::{target})
                                    add_executable({package}::{target} IMPORTED)
                                    set_target_properties({package}::{target} PROPERTIES IMPORTED_LOCATION {exe_path_str})
                                endif()
                                """
                            )

        return config

    def generate(self):
        for filename, content in self.content.items():
            save(
                self, os.path.join(self._conanfile.generators_folder, filename), content
            )
