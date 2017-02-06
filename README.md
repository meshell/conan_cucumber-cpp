[![Build Status](https://travis-ci.org/meshell/cucumber-cpp_conan.svg)](https://travis-ci.org/meshell/cucumber-cpp_conan)

# cucumber-cpp_conan
[conan](https://www.conan.io/) build script for the [Cucumber-cpp](https://github.com/cucumber/cucumber-cpp) framework.


## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

## Upload packages to server

$ conan upload cucumber-cpp/0.3.2@meshell/testing --all

## Reuse the packages

### Basic setup

    $ conan install cucumber-cpp/0.3.2@meshell/testing

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    cucumber-cpp/0.3.2@meshell/testing

    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install .

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
