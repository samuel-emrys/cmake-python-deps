from conan import ConanFile
from conans import tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout

import json
import sys
import os
import textwrap

from pathlib import Path


class CMakePythonDepsConan(ConanFile):
    name = "CMakePythonDeps"
    version = "0.1.0"

    # Optional metadata
    url = "https://github.com/samuel-emrys/cmake-python-deps.git"
    homepage = "https://github.com/samuel-emrys/cmake-python-deps.git"
    license = "MIT"
    description = "A python_requires library providing a CMake generator to expose executables in python virtual environments as CMake targets"
    topics = ("Python", "Virtual Environment", "CMake", "venv")
    no_copy_source = True

    python_requires = "pyvenv/0.1.0"

    def init(self):
        CMakePythonDeps.venv = self.python_requires["pyvenv"].module.PythonVirtualEnv


class CMakePythonDeps(object):
    venv = None

    def __init__(self, conanfile):
        self._conanfile = conanfile

    @property
    def binpath(self):
        return "Scripts" if sys.platform == "win32" else "bin"

    @property
    def content(self):
        config = {}
        for dep_name, user_info in self._conanfile.deps_user_info.items():
            requirements = {}
            virtualenv = self.venv(self._conanfile)
            package_targets = {}
            if "python_requirements" in user_info.vars:
                requirements = json.loads(user_info.python_requirements)

            if "python_envdir" in user_info.vars:
                path = Path(user_info.python_envdir, self.binpath, "python")
                realname = path.resolve(strict=True).name
                interpreter = str(path.with_name(realname))
                virtualenv = self.venv(
                    self._conanfile,
                    python=interpreter,
                    env_folder=user_info.python_envdir,
                )

            for requirement in requirements:
                package = requirement.split("==")[0]
                entry_points = virtualenv.entry_points(package)
                package_targets[package] = entry_points.get("console_scripts", [])

            extension = ""
            if self._conanfile.settings.os == "Windows":
                extension = ".exe"
            for package, targets in package_targets.items():
                for target in targets:
                    exe_path = None
                    for path_ in [
                        Path(self.binpath, f"{target}{extension}"),
                        Path("lib", f"{target}{extension}"),
                    ]:
                        if Path(user_info.python_envdir, path_).is_file():
                            exe_path = Path(user_info.python_envdir, path_)
                            break
                    if not exe_path:
                        self.output.warn(f"Could not find path to {target}{extension}")
                    else:
                        filename = f"{package}-config.cmake"
                        config[filename] = config.get(filename, "") + textwrap.dedent(
                            f"""\
                            if(NOT TARGET {package}::{target})
                                add_executable({package}::{target} IMPORTED)
                                set_target_properties({package}::{target} PROPERTIES IMPORTED_LOCATION {exe_path})
                            endif()
                            """
                        )

        return config

    def generate(self):
        for filename, content in self.content.items():
            tools.save(
                os.path.join(self._conanfile.generators_folder, filename), content
            )
