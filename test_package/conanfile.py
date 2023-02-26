import os
import json
import re

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import cross_building


class PythonVirtualenvTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(
            "python-virtualenv/system@mtolympus/stable",
            options={
                "requirements":json.dumps([
                    "sphinx",
                    "sphinx-rtd-theme",
                ])
             }
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        py = self.python_requires["cmake-python-deps"].module.CMakePythonDeps(self)
        py.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            cmd = f"{os.path.join(self.cpp.build.bindirs[0], 'dumpfile')} 20 {os.path.join(self.build_folder, 'docs', 'sphinx' ,'index.html')}"
            self.run(cmd, env="conanrun")
