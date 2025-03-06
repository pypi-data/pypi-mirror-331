from setuptools import setup, find_packages
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.install import install
import os
import sys
import subprocess
import platform

# 自定义bdist_wheel命令，确保在构建wheel时不编译.so文件
class CustomBdistWheelCommand(bdist_wheel):
    def run(self):
        # 运行原始的bdist_wheel命令
        bdist_wheel.run(self)

# 自定义install命令，在安装后编译.so文件
class CustomInstallCommand(install):
    def run(self):
        # 先运行原始的install命令
        install.run(self)
        
        # 然后编译.so文件
        self.execute(self.compile_so, [], msg="Compiling C extension")
        
    def compile_so(self):
        # 确定包的安装路径
        package_dir = os.path.join(self.install_lib, 'realm_ucp_bootstrap')
        
        # 确定源文件和目标文件的路径
        source_file = os.path.join(package_dir, 'bootstrap_mpi.c')
        
        # 根据平台确定输出文件名
        if platform.system() == 'Windows':
            output_file = os.path.join(package_dir, 'realm_ucp_bootstrap_mpi.dll')
            # Windows上可能需要不同的编译命令
            print("Warning: Windows compilation not fully supported yet")
        else:
            output_file = os.path.join(package_dir, 'realm_ucp_bootstrap_mpi.so')
        
        # 编译命令
        compile_cmd = ['mpicc', '-shared', '-fPIC', source_file, '-o', output_file, '-lmpi']
        
        print(f"Compiling {source_file} to {output_file}")
        try:
            subprocess.check_call(compile_cmd)
            print(f"Successfully compiled {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: mpicc compiler not found. Please ensure MPI is installed.")
            sys.exit(1)

setup(
    name='realm-ucp-bootstrap',
    version='0.1.2',
    description='A Python package that builds and installs an MPI-based shared library',
    author='NVIDIA',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/realm-ucp-bootstrap',
    packages=find_packages(),
    include_package_data=True,
    cmdclass={
        'bdist_wheel': CustomBdistWheelCommand,
        'install': CustomInstallCommand,
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
