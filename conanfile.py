#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake


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
    default_options = "shared=False", "fPIC=True"
    requires = "libpq/9.6.9@bincrafters/stable"
    source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
