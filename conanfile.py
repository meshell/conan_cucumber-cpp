from conans import ConanFile, CMake
from conans import tools
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "meshell")


class CucumberCppConan(ConanFile):
    name = "cucumber-cpp"
    description = "Conan package for the cucumber-cpp C++ BDD framework"
    version = "master"
    folder_name = "cucumber-cpp-{}".format(version)
    settings = ['os', 'compiler', 'build_type', 'arch']
    generators = ['cmake', 'txt']
    url = 'https://github.com/meshell/cucumber-cpp_conan'
    exports = ['CMakeLists.txt', 'FindCuke.cmake', 'CodeCoverageCucumber.cmake']
    license = "https://github.com/cucumber/cucumber-cpp/blob/master/LICENSE.txt"
    options = {
        "disable_boost_test": [True, False],  # Disable boost test driver
        "disable_gtest": [True, False],  # Disable googletest driver
        "use_static_boost": [True, False, None],  # Statically link Boost (except boost::test)
        "include_pdbs": [True, False],
        "cygwin_msvc": [True, False]
    }

    default_options = "disable_boost_test=False", "disable_gtest=False", "use_static_boost=None", "include_pdbs=False", "cygwin_msvc=False"

    build_dir = '_build'
    boost_version = '1.60.0'
    gtest_version = '1.8.0'

    def source(self):
        tar_name = "{}.tar.gz".format(self.folder_name)
        source_tgz = "https://github.com/cucumber/cucumber-cpp/archive/{release}.tar.gz".format(release=self.version)
        self.output.info("Downloading {}".format(source_tgz))
        tools.download(source_tgz, tar_name)
        tools.unzip(tar_name)
        os.unlink(tar_name)

    def requirements(self):
        self.requires("Boost/{boost_version}@lasote/stable".format(boost_version=self.boost_version))
        if not self.options.disable_gtest:
            self.requires("gmock/{gtest_version}@meshell/stable".format(gtest_version=self.gtest_version))
        else:
            self.requires("gmock/{gtest_version}@meshell/stable".format(gtest_version=self.gtest_version), dev=True)

    def config_options(self):
        if self.settings.compiler != "Visual Studio":
            try:  # It might have already been removed if required by more than 1 package
                del self.options.include_pdbs
            except:
                pass

    def configure(self):
        if self.options.use_static_boost is None:
            if self.settings.os == "Windows":
                self.options.use_static_boost = True
            else:
                self.options.use_static_boost = False

    def build(self):
        cmakelist_prepend = '''
            include(${CMAKE_CURRENT_SOURCE_DIR}/../conanbuildinfo.cmake)
            set(CONAN_SYSTEM_INCLUDES ON)
            CONAN_BASIC_SETUP()
            set(GMOCK_ROOT "${CONAN_GTEST_ROOT}")
            set(GTEST_ROOT "${CONAN_GTEST_ROOT}")
            '''
        tools.replace_in_file("{}/CMakeLists.txt".format(self.folder_name), 'project(Cucumber-Cpp)',
                              'project(Cucumber-Cpp CXX C)\n{}'.format(cmakelist_prepend))

        cmake = CMake(self.settings)
        cd_src = "cd {}".format(self.folder_name)
        msdos_shell = (self.settings.os == "Windows") and (not self.options.cygwin_msvc)
        if msdos_shell:
            self.run("{cd_src} && IF not exist {build_dir} mkdir {build_dir}".format(cd_src=cd_src,
                                                                                     build_dir=self.build_dir))
        else:
            self.run("{cd_src} && mkdir -p {build_dir}".format(cd_src=cd_src,
                                                               build_dir=self.build_dir))
        cd_build_cmd = 'cd {src}/{build_dir}'.format(src=self.folder_name,
                                                     build_dir=self.build_dir)
        # BUILD
        flags = ["-DGMOCK_VER={}".format(self.gtest_version)]
        if self.options.disable_boost_test:
            flags.append("-DCUKE_DISABLE_BOOST_TEST=ON")
        if self.options.use_static_boost:
            flags.append("-DCUKE_USE_STATIC_BOOST=ON")
        elif not self.options.use_static_boost:
            flags.append("-DCUKE_USE_STATIC_BOOST=OFF")
        if self.options.disable_gtest:
            flags.append("-DCUKE_DISABLE_GTEST=ON")
        if not (self.scope.dev and self.scope.build_tests):
            flags.append("-DCUKE_DISABLE_UNIT_TESTS=ON")
            flags.append("-DCUKE_DISABLE_E2E_TESTS=ON")

        # JOIN ALL FLAGS
        cxx_flags = " ".join(flags)

        configure_command = '{cd_build} && cmake .. {cmd} {flags}'.format(cd_build=cd_build_cmd,
                                                                          cmd=cmake.command_line,
                                                                          flags=cxx_flags)
        self.output.warn("Configure with: {}".format(configure_command))
        self.run(configure_command)

        self.run("{cd_build} && cmake --build . {build_config}".format(cd_build=cd_build_cmd,
                                                                       build_config=cmake.build_config))

    def package(self):
        self.copy('*', dst='include', src="{src_dir}/include".format(src_dir=self.folder_name), keep_path=True)

        self.copy("FindCuke.cmake", dst='.', src='.')
        self.copy("CodeCoverageCucumber.cmake", dst='.', src='.')

        # Meta files
        self.copy('HISTORY.md', dst='.', src=self.folder_name, keep_path=True)
        self.copy('LICENSE.txt', dst='.', src=self.folder_name, keep_path=True)
        self.copy('README.md', dst='.', src=self.folder_name, keep_path=True)

        # Copying static and dynamic libs
        self.copy(pattern="*.a", dst="lib", src='{}/{}/lib'.format(self.folder_name, self.build_dir), keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src='{}/{}/lib'.format(self.folder_name, self.build_dir), keep_path=False)

        # Copying debug symbols
        if self.settings.compiler == "Visual Studio" and self.options.include_pdbs:
            self.copy(pattern="*.pdb", dst="lib", src='{}/{}/lib'.format(self.folder_name, self.build_dir),
                      keep_path=False)

    def package_info(self):
        self.cpp_info.libs.append('cucumber-cpp')
        if self.settings.os == "Windows":
            self.cpp_info.libs.append('ws2_32')
        else:
            self.cpp_info.cppflags = ["-pthread"]
