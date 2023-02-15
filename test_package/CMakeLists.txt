cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

# Executable that prints out the contents of sphinx build artefact index.html
add_executable(dumpfile src/dumpfile.cpp)

# The interesting detail for this test_package is in docs/CMakeLists.txt
add_subdirectory("docs")
