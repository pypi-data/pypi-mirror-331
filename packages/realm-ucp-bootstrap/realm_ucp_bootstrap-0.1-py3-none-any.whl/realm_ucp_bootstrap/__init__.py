import os

lib_path = os.path.join(os.path.dirname(__file__), "realm_ucp_bootstrap_mpi.so")

def get_library_path():
    return lib_path
