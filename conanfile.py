from conans import ConanFile, CMake
from conans import tools
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "meshell")


class CucumberCppConan(ConanFile):
    name = "cucumber-cpp"
    version = "0.3.2rc1"
    folder_name = "cucumber-cpp-{}".format(version)
    settings = ['os', 'compiler', 'build_type', 'arch']
    generators = ['cmake', 'txt']
    url = 'https://github.com/meshell/cucumber-cpp_conan'
    exports = ['CMakeLists.txt', 'FindCuke.cmake', 'CodeCoverageCucumber.cmake']
    license = "https://github.com/cucumber/cucumber-cpp/blob/master/LICENSE.txt"
    options = {
        "disable_boost_test": ['ON', 'OFF'],  # Statically link Boost (except boost::test)
        "disable_gtest": ['ON', 'OFF'],  # Disable boost:test
        "use_static_boost": ['ON', 'OFF']  # Disable Google Test framework
    }
    default_options = "disable_boost_test=OFF", "disable_gtest=OFF", "use_static_boost=OFF"

    build_dir = '_build'
    boost_version = '1.60.0'
    gtest_version = '1.8.0'

    def source(self):
        tar_name = "{}.tar.gz".format(self.folder_name)
        source_tgz = "https://github.com/meshell/cucumber-cpp/archive/v{release}.tar.gz".format(release=self.version)
        self.output.info("Downloading {}".format(source_tgz))
        tools.download(source_tgz, tar_name)
        tools.unzip(tar_name)
        os.unlink(tar_name)

    def requirements(self):
        self.requires("Boost/{boost_version}@lasote/stable".format(boost_version=self.boost_version))
        if not self.options.disable_gtest:
            self.requires("gtest/{gtest_version}@lasote/stable".format(gtest_version=self.gtest_version))
        else:
            self.requires("gtest/{gtest_version}@lasote/stable".format(gtest_version=self.gtest_version), dev=True)

    def config(self):
        if self.settings.os == "Windows":
            self.options.use_static_boost = 'ON'

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
            self.run("{cd_src} && IF not exist {}/{build_dir} mkdir {build_dir}".format(cd_src=cd_src,
                                                                                        build_dir=self.build_dir))
        else:
            self.run("{cd_src} && mkdir -p {build_dir}".format(cd_src=cd_src,
                                                               build_dir=self.build_dir))
        cd_build_cmd = 'cd {src}/{build_dir}'.format(src=self.folder_name,
                                                     build_dir=self.build_dir)
        # BUILD
        flags = "-DGMOCK_VER={gmock_ver} -DCUKE_DISABLE_BOOST_TEST={disable_boost_test} -DCUKE_USE_STATIC_BOOST={use_static_boost} -DCUKE_DISABLE_GTEST={disable_gtest}".format(
            gmock_ver=self.gtest_version,
            disable_boost_test=self.options.disable_boost_test,
            use_static_boost=self.options.use_static_boost,
            disable_gtest=self.options.disable_gtest)
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
        # self.copy('*', dst='cmake', src="{src_dir}/cmake".format(src_dir=self.name), keep_path=True)
        self.copy('*', dst='include', src="{src_dir}/include".format(src_dir=self.folder_name), keep_path=True)
        # self.copy('*', dst='src', src="{src_dir}/src".format(src_dir=self.name), keep_path=True)

        # self.copy('Gemfile', dst='.', src=self.name, keep_path=True)
        # self.copy('CMakeLists.txt', dst='.', src=self.name, keep_path=True)
        self.copy("FindCuke.cmake", dst='.', src='.')

        # Meta files
        self.copy('HISTORY.md', dst='.', src=self.folder_name, keep_path=True)
        self.copy('LICENSE.txt', dst='.', src=self.folder_name, keep_path=True)
        self.copy('README.md', dst='.', src=self.folder_name, keep_path=True)

        self.copy("*.lib", dst='lib', src='{}/{}/lib'.format(self.folder_name, self.build_dir))
        self.copy("*.a", dst="lib", src='{}/{}/lib'.format(self.folder_name, self.build_dir))

    def _copy_visual_binaries(self):
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs.append('cucumber-cpp')
