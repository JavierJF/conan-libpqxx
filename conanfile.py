#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, CMake
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration


class LibpqxxRecipe(ConanFile):
    name = "libpqxx"
    version = "6.2.4"
    settings = "os", "compiler", "build_type", "arch"
    description = "The official C++ client API for PostgreSQL"
    url = "https://github.com/bincrafters/conan-libpqxx"
    homepage = "https://github.com/jtv/libpqxx"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3"
    generators = "cmake"
    exports = "LICENSE.md"
    exports_sources = "CMakeLists.txt"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "libpq/10.4@philabs/stable"
    _source_subfolder = "source_subfolder"
    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        if self.settings.os == "Windows" and \
           self.settings.compiler == "Visual Studio" and \
           Version(self.settings.compiler.version.value) < "14":
            raise ConanInvalidConfiguration("Your MSVC version is too old, libpqxx requires C++14")

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = [
                "--disable-documentation",
                "--with-postgres-include={}".format(os.path.join(self.deps_cpp_info["libpq"].rootpath, "include")),
                "--with-postgres-lib={}".format(os.path.join(self.deps_cpp_info["libpq"].rootpath, "lib")),
                "--enable-static={}".format("no" if self.options.shared else "yes"),
                "--enable-shared={}".format("yes" if self.options.shared else "no")
            ]
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            env_vars = self._autotools.vars
            self._autotools.configure(args=args, vars=env_vars)
        return self._autotools

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("Ws2_32")
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
