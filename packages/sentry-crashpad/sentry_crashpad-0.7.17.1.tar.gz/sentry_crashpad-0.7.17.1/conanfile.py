import re

from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, cmake_layout


class SentryCrashpadRecipe(ConanFile):
    name = "sentry-crashpad"
    package_type = "library"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True,
        "sentry-native/*:backend": "crashpad",
    }

    def requirements(self):
        with open("sentry_version.txt", "r") as f:
            sentry_version = f.read().strip()
            match = re.match(r"^([0-9]+)\.([0-9]+)\.([0-9]+)", sentry_version)
            assert match
            sentry_version = match.group(0)

        self.requires(f"sentry-native/{sentry_version}")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()
