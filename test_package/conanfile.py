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
    ruby_version = "2.4.0"

    def system_requirements(self):
        def _install_ruby_build_dependencies(installer):
            dependencies = ["build-essential", "libreadline-dev", "libssl-dev", "zlib1g-dev"]
            for dependency in dependencies:
                installer.install(dependency)

        def _install_rbenv_linux():
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

        def _install_rbenv_mcosx(installer):
            installer.install("rbenv")
            os.environ["RBENV_ROOT"] = os.path.join("usr", "local", "var", "rbenv")
            self.run('eval "$(rbenv init -)"')
            installer.install("ruby-build")
            installer.install("rbenv-bundler")

        def _install_rbenv():
            installer = SystemPackageTool()
            installer.update()  # Update the package database
            if os_info.is_linux:
                _install_ruby_build_dependencies(installer)
                _install_rbenv_linux()
            elif os_info.is_macos:
                _install_rbenv_mcosx(installer)

        def _install_and_use_ruby(version):
            # Install rbenv for managing enabling of multiple rubies.
            self.run("rbenv install -s {} && rbenv rehash".format(version))
            self.run("rbenv global {} && rbenv rehash".format(version))
            self.run("ruby --version")

        def _install_gem(gem):
            self.run("gem install --no-document {}".format(gem))
            self.run("rbenv rehash")

        self.global_system_requirements = True
        if os_info.is_linux or os_info.is_macos:
            _install_rbenv()
            _install_and_use_ruby(self.ruby_version)
            _install_gem("bundler")

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
