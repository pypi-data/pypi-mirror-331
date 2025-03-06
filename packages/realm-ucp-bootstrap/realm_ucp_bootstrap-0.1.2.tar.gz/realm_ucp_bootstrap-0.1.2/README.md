# realm-ucp-bootstrap

一个Python包，用于构建和安装基于MPI的共享库。该包在安装过程中会编译C源代码并生成共享库文件。

## 前提条件

- Python 3.6+
- MPI库和编译器（如OpenMPI或MPICH）
- C编译器（如gcc）

## 安装

```bash
# 从PyPI安装
pip install realm-ucp-bootstrap

# 或从源代码安装
git clone https://github.com/yourusername/realm-ucp-bootstrap.git
cd realm-ucp-bootstrap
pip install .
```

## 使用方法

```python
import realm_ucp_bootstrap

# 获取共享库路径
lib_path = realm_ucp_bootstrap.get_library_path()
print(f"共享库路径: {lib_path}")

# 使用ctypes加载共享库
import ctypes
lib = ctypes.CDLL(lib_path)
```

## 开发

如果您想参与开发，请按照以下步骤操作：

```bash
git clone https://github.com/yourusername/realm-ucp-bootstrap.git
cd realm-ucp-bootstrap
pip install -e .
```

## 许可证

Apache License 2.0
