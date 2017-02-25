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
    options = {
        "ruby_version": ["1.9.3-p551", "2.0.0-p648",
                         "2.1.0", "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5",
                         "2.1.6", "2.1.7", "2.1.8", "2.1.9", "2.1.10",
                         "2.2.0", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "2.2.5",
                         "2.2.6", "2.3.0", "2.3.1", "2.3.2", "2.3.3", "2.4.0"]
    }

    default_options = "ruby_version=2.4.0"

    def system_requirements(self):
        def _install_ruby_build_dependencies():
            installer = SystemPackageTool()
            installer.update()  # Update the package database
            dependencies = ["build-essential", "libreadline-dev", "libssl-dev", "zlib1g-dev"]
            for dependency in dependencies:
                installer.install(dependency)

        def _install_rbenv():
            _install_ruby_build_dependencies()
            # Install and setup rbenv
            home_dir = os.environ["HOME"]
            rbenv_path = os.path.join(home_dir, ".rbenv")
            if not os.path.exists(rbenv_path):
                self.run("git clone git://github.com/sstephenson/rbenv.git {}".format(rbenv_path))
            path_env = os.path.join(rbenv_path, "shims")
            path_env += os.pathsep + os.path.join(rbenv_path, "bin")
            if not path_env in os.environ["PATH"]:
                path_env += os.pathsep + os.environ["PATH"]
                os.environ["PATH"] = path_env

            ruby_build_path = os.path.join(rbenv_path, "plugins", "ruby-build")
            if not os.path.exists(ruby_build_path):
                self.run("git clone git://github.com/sstephenson/ruby-build.git {}".format(ruby_build_path))
            ruby_build_bin_path = os.path.join(ruby_build_path, "bin")
            if not ruby_build_bin_path in os.environ["PATH"]:
                ruby_build_bin_path += os.pathsep + os.environ["PATH"]
                os.environ["PATH"] = ruby_build_bin_path

            rbenv_bundler_path = os.path.join(rbenv_path, "plugins", "bundler")
            if not os.path.exists(rbenv_bundler_path):
                self.run("git clone git://github.com/carsomyr/rbenv-bundler.git {}".format(rbenv_bundler_path))

        def _install_and_use_ruby(version):
            # Install rbenv for managing enabling of multiple rubies.
            self.run("rbenv install -s {} && rbenv rehash".format(version))
            self.run("rbenv local {} && rbenv rehash".format(version))
            self.run("ruby --version")

        def _install_gem(gem):
            gem_options = []
            if self.options.ruby_version == "1.9.3-p551":
                gem_options.append("--no-rdoc")
                gem_options.append("--no-ri")
            else:
                gem_options.append("--no-document")
            self.run("gem install {} {}".format(" ".join(gem_options), gem))
            self.run("rbenv rehash")

        if not os_info.is_windows:
            _install_rbenv()
            _install_and_use_ruby(self.options.ruby_version)
            # install bundler
            _install_gem("bundler")

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "{}" {}'.format(self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . {}".format(cmake.build_config))

    def test(self):
        if os_info.is_windows:
            pass
        else:
            self.run("ruby --version")
            cmake = CMake(self.settings)
            self.run("cmake --build . --target run_feature_test {}".format(cmake.build_config))
