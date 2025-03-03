# -*- coding: utf-8 -*-
#    BoltzTraP2, a program for interpolating band structures and calculating
#    semi-classical transport coefficients.
#    Copyright (C) 2017-2025 Georg K. H. Madsen <georg.madsen@tuwien.ac.at>
#    Copyright (C) 2017-2025 Jesús Carrete <jesus.carrete.montana@tuwien.ac.at>
#    Copyright (C) 2017-2025 Matthieu J. Verstraete <matthieu.verstraete@ulg.ac.be>
#    Copyright (C) 2018-2019 Genadi Naydenov <gan503@york.ac.uk>
#    Copyright (C) 2020 Gavin Woolman <gwoolma2@staffmail.ed.ac.uk>
#    Copyright (C) 2020 Roman Kempt <roman.kempt@tu-dresden.de>
#    Copyright (C) 2022 Robert Stanton <stantor@clarkson.edu>
#    Copyright (C) 2024 Haoyu (Daniel) Yang <yanghaoyu97@outlook.com>
#
#    This file is part of BoltzTraP2.
#
#    BoltzTraP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BoltzTraP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BoltzTraP2. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import contextlib
import os
import platform
import shutil
import subprocess
import tempfile
from os import PathLike

import numpy as np
from Cython.Build import cythonize
from setuptools import Command, Extension, setup
from setuptools.command.build_ext import build_ext as DefaultBuildExtCommand

# Set this to True to regenerate BoltzTraP2/sphere/frontend.cpp from its
# Cython sources as part of the build process.
USE_CYTHON: bool = True

# Extra header and library dirs for compiling the C and C++ source files.
INCLUDE_DIRS: list[PathLike] = []
LIBRARY_DIRS: list[PathLike] = []

EIGEN_DIR: PathLike = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "external", "eigen-eigen-3215c06819b9"
    )
)


@contextlib.contextmanager
def dir_context(dn):
    """Create a context with a given directory as the CWD."""
    # Sabe the original CWD.
    original = os.getcwd()
    try:
        # Change to the new directory and return control.
        os.chdir(dn)
        yield
    finally:
        # Change back to the original directory.
        os.chdir(original)


class CleanSPGlibCommand(Command):
    """Custom command used to clean the spglib directory."""

    description = "remove libsymspg.a and all old spglib build directores"
    user_options = []

    def initialize_options(self):
        """Do nothing."""

    def finalize_options(self):
        """Do nothing."""

    def run(self):
        """Remove libsymspg.a and all spglib build directores."""
        self.announce("About to remove libsymspg.a", level=1)
        try:
            os.remove(BuildSPGlibCommand.static_library)
        except FileNotFoundError:
            self.announce("libsymspg.a did not exist", level=1)
        self.announce(
            "About to remove all old spglib build directories", level=1
        )
        with dir_context(BuildSPGlibCommand.base_dir):
            build_dirs = [i for i in glob.glob("build-*") if os.path.isdir(i)]
            for d in build_dirs:
                shutil.rmtree(d, ignore_errors=True)


class BuildSPGlibCommand(Command):
    """Custom command used to compile a local static copy of spglib."""

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "external", "spglib-1.9.9")
    )
    header_dir = os.path.join(base_dir, "src")
    if platform.system() == "Windows":
        static_library_basename = "symspg.lib"
        static_library_trailing = os.path.join(
            "Release", static_library_basename
        )
    else:
        static_library_basename = "libsymspg.a"
        static_library_trailing = static_library_basename
    static_library = os.path.join(base_dir, static_library_basename)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run cmake with the right options, and then run make."""
        if os.path.isfile(self.static_library):
            self.announce("the static library exists, no need to rebuild it")
            return
        self.announce(
            "About to create a new build directory for spglib", level=1
        )
        build_dir = tempfile.mkdtemp(
            prefix="build-", dir=BuildSPGlibCommand.base_dir
        )
        self.announce("About to run 'cmake' for spglib", level=1)
        with dir_context(BuildSPGlibCommand.base_dir):
            subprocess.check_call(
                [
                    "cmake",
                    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
                    "-S",
                    ".",
                    "-B",
                    build_dir,
                ]
            )
        self.announce("About to build spglib", level=1)
        with dir_context(BuildSPGlibCommand.base_dir):
            tokens = ["cmake", "--build", build_dir]
            if platform.system() == "Windows":
                tokens += ["--config", "Release"]
            subprocess.check_call(tokens)
            shutil.copy2(
                os.path.join(
                    build_dir, BuildSPGlibCommand.static_library_trailing
                ),
                BuildSPGlibCommand.base_dir,
            )
        self.announce("About to remove the spglib build directory", level=1)
        shutil.rmtree(build_dir)


class BuildExtCommand(DefaultBuildExtCommand):
    """Custom build_ext command that will build spglib first."""

    system_specific_flags = {
        "Darwin": ["-std=c++11", "-stdlib=libc++"],
        "Linux": ["-std=c++11"],
        "Windows": ["/std:c++14"],
    }

    def build_extensions(self):
        self.announce("About to test compiler flags")
        # only add flags which pass the flag_filter
        try:
            opts = BuildExtCommand.system_specific_flags[platform.system()]
        except KeyError:
            opts = []
        for ext in self.extensions:
            ext.extra_compile_args = opts
        super().build_extensions()

    def run(self):
        """Run build_spglib and then delegate on the normal build_ext."""
        self.run_command("build_spglib")
        super().run()


extensions = [
    Extension(
        name="BoltzTraP2.sphere.frontend",
        sources=[
            "BoltzTraP2/sphere/frontend." + ("pyx" if USE_CYTHON else "cpp"),
            "BoltzTraP2/sphere/backend.cpp",
        ],
        language="c++",
        include_dirs=INCLUDE_DIRS
        + [np.get_include(), BuildSPGlibCommand.header_dir, EIGEN_DIR],
        library_dirs=LIBRARY_DIRS,
        runtime_library_dirs=LIBRARY_DIRS,
        extra_objects=[BuildSPGlibCommand.static_library],
    )
]

setup(
    ext_modules=cythonize(extensions) if USE_CYTHON else extensions,
    cmdclass={
        "build_ext": BuildExtCommand,
        "build_spglib": BuildSPGlibCommand,
        "clean_spglib": CleanSPGlibCommand,
    },
)
