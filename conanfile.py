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
        "use_static_boost": [True, False],  # Statically link Boost (except boost::test)
        "include_pdbs": [True, False],
        "cygwin_msvc": [True, False]
    }

    default_options = "disable_boost_test=False", "disable_gtest=False", "use_static_boost=False", "include_pdbs=False", "cygwin_msvc=False"

    build_dir = '_build'
    boost_version = '1.60.0'
    gtest_version = '1.8.0'

    @staticmethod
    def _make_cmake_bool(value):
        return "ON" if value else "OFF"

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
            self.requires("gmock/{gtest_version}@meshell/testing".format(gtest_version=self.gtest_version))
        else:
            self.requires("gmock/{gtest_version}@meshell/testing".format(gtest_version=self.gtest_version), dev=True)

    def config_options(self):
        # use libstdc++11 on gcc > 5.1
        if self.settings.compiler == 'gcc' and float(self.settings.compiler.version.value) >= 5.1:
            self.settings.compiler.libcxx = 'libstdc++11'
        if self.settings.os == "Windows":
            self.options.use_static_boost = True
        if self.settings.compiler != "Visual Studio":
            try:  # It might have already been removed if required by more than 1 package
                del self.options.include_pdbs
            except:
                pass

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
        msdos_shell = (self.settings.os == "Windows") and (self.options.cygwin_msvc == False)
        if msdos_shell:
            self.run("{cd_src} && IF not exist {build_dir} mkdir {build_dir}".format(cd_src=cd_src,
                                                                                     build_dir=self.build_dir))
        else:
            self.run("{cd_src} && mkdir -p {build_dir}".format(cd_src=cd_src,
                                                               build_dir=self.build_dir))
        cd_build_cmd = 'cd {src}/{build_dir}'.format(src=self.folder_name,
                                                     build_dir=self.build_dir)
        # BUILD
        flags = "-DGMOCK_VER={gmock_ver} -DCUKE_DISABLE_BOOST_TEST={disable_boost_test} -DCUKE_USE_STATIC_BOOST={use_static_boost} -DCUKE_DISABLE_GTEST={disable_gtest}".format(
            gmock_ver=self.gtest_version,
            disable_boost_test=self._make_cmake_bool(self.options.disable_boost_test),
            use_static_boost=self._make_cmake_bool(self.options.use_static_boost),
            disable_gtest=self._make_cmake_bool(self.options.disable_gtest))
        flag_no_tests = "" if self.scope.dev and self.scope.build_tests else "-DCUKE_DISABLE_UNIT_TESTS=ON -DCUKE_DISABLE_E2E_TESTS=ON"
        configure_command = '{cd_build} && cmake .. {cmd} {flags} {flag_no_tests}'.format(cd_build=cd_build_cmd,
                                                                                          cmd=cmake.command_line,
                                                                                          flags=flags,
                                                                                          flag_no_tests=flag_no_tests)
        self.output.warn("Configure with: {}".format(configure_command))
        self.run(configure_command)

        self.run("{cd_build} && cmake --build . {build_config}".format(cd_build=cd_build_cmd,
                                                                       build_config=cmake.build_config))

    def package(self):
        self.copy('*', dst='include', src="{src_dir}/include".format(src_dir=self.folder_name), keep_path=True)

        self.copy("FindCuke.cmake", dst='.', src='.')

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
