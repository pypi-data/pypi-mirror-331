import os
from PyInstaller.utils.hooks import collect_dynamic_libs

hiddenimports = ['llama_cpp.llama_cpp', 'llama_cpp._ctypes_extensions']
datas = []
binaries = []

# Add the shared library
lib_dir = os.path.dirname(__import__('llama_cpp').__file__)
for lib in collect_dynamic_libs('llama_cpp'):
    binaries.append(lib) 