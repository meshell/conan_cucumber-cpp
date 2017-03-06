from conans import ConanFile, CMake
from conans.tools import os_info, SystemPackageTool
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "meshell")


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    requires = "cucumber-cpp/master@{}/{}".format(username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "{}" {}'.format(self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . {}".format(cmake.build_config))

    def test(self):
        if os_info.is_linux or os_info.is_macos:
            self.run("ruby --version")
            cmake = CMake(self.settings)
            self.run("cmake --build . --target run_feature_test {}".format(cmake.build_config))
        else:
            pass
