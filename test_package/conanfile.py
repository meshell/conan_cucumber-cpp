from conans import ConanFile, CMake
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "meshell")


class CucumberCppFeatureConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "cucumber-cpp/0.3.2rc1@{}/{}".format(username, channel)
    generators = "cmake"

    def _install_rubygems(self):
        self.run('sudo apt-get install -y ruby1.9.2 rubygems1.9.2')
        self.run('sudo gem install bundler')

    def build(self):
        self._install_rubygems()
        cmake = CMake(self.settings)
        self.run('cmake "{}" {}'.format(self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . {}".format(cmake.build_config))

    def test(self):
        cmake = CMake(self.settings)
        self.run("cmake --build . --target run_feature_test {}".format(cmake.build_config))
