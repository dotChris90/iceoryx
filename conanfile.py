from conans import ConanFile, CMake, tools
import os
from conans.tools import load
from pathlib import Path

def get_toml_line():
    return "add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/cmake/cpptoml/ ${CMAKE_BINARY_DIR}/dependencies/posh/cpptoml/prebuild)"

def get_version():
    try:
        return load("VERSION")
    except Exception as e:
        return "ERROR"

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
    default_options['toml_config'] = True
    exports_sources = ["*"]
    generators = ["cmake"]
    cmake = None   

    def __adapt_cmakefile(self):
        tools.replace_in_file("iceoryx_meta/CMakeLists.txt", "project(iceoryx_meta)",
                              '''project(iceoryx_meta)
include(${CONAN_BUILD_INFO_FILE})
conan_basic_setup()''')

    def __add_definitions_of_dependencies(self):
        if self.options.toml_config:
            toml_lib    = [folder for idx, folder in enumerate(self.deps_cpp_info.libdirs) if "cpptoml/master" in folder][0]
            toml_cmkae  = str(Path(toml_lib).joinpath("cmake/cpptoml"))
            self.cmake.definitions["cpptoml_DIR"] = toml_cmkae

    def __patch_cmake_toml(self):
        tools.replace_in_file("iceoryx_posh/CMakeLists.txt", get_toml_line(),
                              "#" + get_toml_line())

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.toml_config:
            cmd = "git clone https://github.com/jgsogo/conan-cpptoml.git"
            os.system(cmd)
            cmd = "cd conan-cpptoml && conan export . "
            os.system(cmd)
            self.requires("cpptoml/master")  

    def build(self):
        conanbuildinfo_file = str(Path(os.getcwd()).joinpath("conanbuildinfo.cmake").absolute())
        self.__adapt_cmakefile()
        if self.options.toml_config:
            self.__patch_cmake_toml()

        self.cmake = CMake(self)
        self.cmake.definitions["CMAKE_INSTALL_PREFIX"]  = "./target"
        self.cmake.definitions["BUILD_SHARED_LIBS"]     = "ON" if self.options.shared         else "OFF"
        self.cmake.definitions["TOML_CONFIG"]           = "ON" if self.options.toml_config    else "OFF"
        self.cmake.definitions["CONAN_BUILD_INFO_FILE"] = conanbuildinfo_file
        
        self.__add_definitions_of_dependencies()
        
        self.cmake.configure(build_folder="build",source_folder="iceoryx_meta")
        self.cmake.build()

    def package(self):
        self.cmake.install()
        self.copy("*.hpp",      dst="include",  src="build/target/include/")
        self.copy("*.so",       dst="lib",      src="build/target/lib/")
        self.copy("*.a",        dst="lib",      src="build/target/lib/")
        self.copy("*",          dst="bin",      src="build/target/bin/")
        self.copy("*",          dst="etc",      src="build/target/etc/")

    def package_info(self):
        self.cpp_info.libs = [
            "iceoryx_binding_c",
            "iceoryx_platform",
            "iceoryx_posh",
            "iceoryx_posh_gateway",
            "iceoryx_posh_roudi"
            "iceoryx_utils"
            ]

