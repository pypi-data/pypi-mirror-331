from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import os

class BuildMPIExt(build_py):
    def run(self):
        package_dir = os.path.join(self.build_lib, "realm_ucp_bootstrap")
        os.makedirs(package_dir, exist_ok=True)

        output_so = os.path.join(package_dir, "realm_ucp_bootstrap_mpi.so")

        # 编译 .so
        subprocess.check_call(
            ["mpicc", "-shared", "-fPIC", "realm_ucp_bootstrap/bootstrap_mpi.c", "-o", output_so, "-lmpi"]
        )

        # 继续默认的 build_py 操作
        super().run()

setup(
    name="realm-ucp-bootstrap",
    version="0.1",
    packages=["realm_ucp_bootstrap"],
    cmdclass={"build_py": BuildMPIExt},  # 在 build_py 阶段编译
    package_data={"realm_ucp_bootstrap": ["realm_ucp_bootstrap_mpi.so"]},
    include_package_data=True,
)