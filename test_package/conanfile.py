import os
import json
import re

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import cross_building

def get_version():
    # Read the version from the parent conanfile.py
    # TODO: Remove this when conan 2.0 is usable. This is unnecessary in conan 2.0
    with open("../conanfile.py", "r") as f:
        conanfile = f.read()
    regx = re.compile("\d\.\d\.\d")
    version = regx.findall(conanfile)[0]
    return version

class PythonVirtualenvTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False
    test_type = "explicit"

    # TODO: Remove in 2.0. This restricts the testable user/channel due to 
    # limitations in 1.x
    python_requires = f"CMakePythonDeps/{get_version()}@mtolympus/stable"

    def configure(self):
        self.options["python-virtualenv"].requirements = json.dumps([
            "sphinx",
            "sphinx-rtd-theme",
        ])

    def build_requirements(self):
        self.tool_requires("python-virtualenv/system@mtolympus/stable")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        py = self.python_requires["CMakePythonDeps"].module.CMakePythonDeps(self)
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
