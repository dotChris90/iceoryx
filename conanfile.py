from conans import ConanFile, CMake, tools
import os
from conans.tools import load
import shutil

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
    generators = ["cmake"]
    cmake = None   

    def __adapt_cmakefile(self):
        tools.replace_in_file("iceoryx_meta/CMakeLists.txt", "project(iceoryx_meta)",
                              '''project(iceoryx_meta)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        #shutil.copyfile("conanbuildinfo.cmake","iceoryx_meta/conanbuildinfo.cmake")
        #self.__adapt_cmakefile()

        self.cmake = CMake(self)
        self.cmake.definitions["CMAKE_INSTALL_PREFIX"]  = "./target"
        self.cmake.definitions["BUILD_SHARED_LIBS"]     = "ON" if self.options.shared         else "OFF"
        self.cmake.definitions["TOML_CONFIG"]           = "ON" if self.options.toml_config    else "OFF"
        self.cmake.configure(build_folder="build",source_folder="iceoryx_meta")
        self.cmake.build()

    def package(self):
        self.cmake.install()
        self.copy("*.hpp",      dst="include",  src="build/target/include/")
        self.copy("*.so",       dst="lib",      src="build/target/lib/")
        self.copy("*.a",        dst="lib",      src="build/target/lib/")

    def package_info(self):
        self.cpp_info.libs = [
            "iceoryx_binding_c",
            "iceoryx_platform",
            "iceoryx_posh",
            "iceoryx_posh_gateway",
            "iceoryx_posh_roudi"
            "iceoryx_utils"
            ]

