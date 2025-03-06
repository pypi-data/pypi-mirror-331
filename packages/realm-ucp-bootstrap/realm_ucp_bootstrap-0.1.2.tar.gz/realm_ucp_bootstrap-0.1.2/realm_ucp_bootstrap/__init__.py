import os
import platform

# 确定库文件的路径
if platform.system() == 'Windows':
    lib_name = "realm_ucp_bootstrap_mpi.dll"
else:
    lib_name = "realm_ucp_bootstrap_mpi.so"

lib_path = os.path.join(os.path.dirname(__file__), lib_name)

def get_library_path():
    """返回编译后的共享库路径"""
    if not os.path.exists(lib_path):
        raise ImportError(f"找不到共享库: {lib_path}。请确保MPI已安装，并且包安装过程中正确编译了C文件。")
    return lib_path

__version__ = '0.1.1'
