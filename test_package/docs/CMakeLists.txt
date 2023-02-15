# CMakePythonDeps generates a target for the python package name
find_package(sphinx REQUIRED)

# Sphinx configuration
set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR})
set(SPHINX_BUILD ${CMAKE_CURRENT_BINARY_DIR}/sphinx)
set(SPHINX_INDEX_FILE ${SPHINX_BUILD}/index.html)

# CMakePythonDeps generates a component for each binary exported by the python package
# In this case, it will invoke sphinx-build
add_custom_command(
  OUTPUT ${SPHINX_INDEX_FILE}
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/index.rst
  COMMAND sphinx::sphinx-build -b html ${SPHINX_SOURCE} ${SPHINX_BUILD}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Generating documentation with Sphinx")

add_custom_target(Sphinx ALL DEPENDS ${SPHINX_INDEX_FILE})

# Add an install target to install the docs
include(GNUInstallDirs)
install(DIRECTORY ${SPHINX_BUILD}/ DESTINATION ${CMAKE_INSTALL_DOCDIR})

