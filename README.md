[![Build Status Travis](https://travis-ci.org/meshell/conan_cucumber-cpp.svg)](https://travis-ci.org/meshell/conan_cucumber-cpp)
[![Build status AppVeyor](https://ci.appveyor.com/api/projects/status/87xtvnlff3gef1ja?svg=true)](https://ci.appveyor.com/project//meshell/conan_cucumber-cpp)


# conan_cucumber-cpp
[conan](https://www.conan.io/) package for the [cucumber-cpp](https://github.com/cucumber/cucumber-cpp) framework.

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/cucumber-cpp/master/meshell/testing).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

## Upload packages to server

    $ conan upload cucumber-cpp/master@meshell/testing --all

## Reuse the packages

### Basic setup

    $ conan install cucumber-cpp/master@meshell/testing

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    cucumber-cpp/master@meshell/testing

    [options]
    cucumber-cpp:disable_boost_test=true  # Disable boosttest driver
    cucumber-cpp:disable_gtest=false      # Disable googletest driver
    cucumber-cpp:use_static_boost=false   # Statically link Boost (except boost::test)
    cucumber-cpp:include_pdbs=false       # MSVC - include debug symbols

    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install .

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
