from conans import ConanFile, CMake, tools
import os
from conans.tools import load
import re

def get_version():
    try:
        content = load("VERSION")
        version = content
        return version
    except Exception as e:
        return None

class IceoryxConan(ConanFile):
    name = "iceoryx"
    version = get_version()
    license = "Apache License 2.0"
    homepage = "https://iceoryx.io/v1.0.0/"
    url = "https://github.com/eclipse-iceoryx/iceoryx.git"
    description = "Eclipse iceoryx™ - true zero-copy inter-process-communication"
    topics = ("Shared Memory", "IPC","ROS")
    settings = "os", "compiler", "build_type", "arch"
    options = { "fPIC": [True, False]}
    options['toml_config'] = [True,False]
    options["shared"] = [True,False]
    default_options = { "fPIC": True}
    default_options["shared"] = False
    default_options['toml_config'] = False
    exports_sources = ["*"]
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.toml_config == True:
            raise NotImplementedError()

    def build(self):
        cmd = "cmake "
        if self.options.shared:
            cmd = cmd + " -DBUILD_SHARED_LIBS=ON "
        cmd = cmd + " -DCMAKE_INSTALL_PREFIX=./target -Bbuild -Hiceoryx_meta -DTOML_CONFIG=OFF"
        os.system(cmd)
        cmd = "cmake --build build"
        os.system(cmd)
        cmd = "cmake --build build --target install"
        os.system(cmd)
        

    def package(self):
        self.copy("*.hpp",      dst="include",  src="target/include/")
        self.copy("*.so",       dst="lib",      src="target/lib/")
        self.copy("*.a",        dst="lib",      src="target/lib/")

    def package_info(self):
        self.cpp_info.libs = [
            "iceoryx_binding_c",
            "iceoryx_platform",
            "iceoryx_posh",
            "iceoryx_posh_gateway",
            "iceoryx_posh_roudi"
            "iceoryx_utils"
            ]

