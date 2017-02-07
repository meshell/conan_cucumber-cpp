from conans import ConanFile, CMake
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "meshell")


class CucumberCppFeatureConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "cucumber-cpp/master@{}/{}".format(username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "{}" {}'.format(self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . {}".format(cmake.build_config))

    def test(self):
        # running tests would require ruby
        pass
