import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        # 调用父类的 run 方法，继续执行标准安装步骤
        install.run(self)
        # 在安装过程中执行自定义脚本
        print("执行自定义脚本...")

        # 定义脚本路径
        data_path = os.path.join(os.path.dirname(__file__), 'ascend', 'Ascend-cann-nnrt_8.0.0_linux-aarch64.run')

        # 检查脚本是否存在
        if os.path.exists(data_path):
            print(f"执行脚本：{data_path}")
            # 执行包内的脚本
            cmd = 'printf "Y\n" | bash {} --install'.format(data_path)
            subprocess.check_call(cmd, shell=True)
        else:
            print(f"脚本 {data_path} 未找到！")

setup(
    name="ascend-cann-nnrt",
    version="8.0.0",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "attrs",
        "cython",
        "numpy==1.24.0",
        "decorator",
        "sympy",
        "cffi",
        "pyyaml",
        "pathlib2",
        "psutil",
        "protobuf==3.20",
        "scipy",
        "requests",
        "absl-py",
    ],
    cmdclass={"install": CustomInstall},
)

