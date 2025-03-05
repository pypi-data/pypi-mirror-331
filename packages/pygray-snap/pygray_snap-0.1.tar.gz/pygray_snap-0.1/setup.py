import os
from setuptools import setup, Extension, find_packages
from setuptools.command.install import install


class CustomInstall(install):
    def run(self):
        super().run()
        package_dir = os.path.join(self.install_lib, "pygray_snap")
        source_file = os.path.join(package_dir, "core.c")
        if os.path.exists(source_file):
            try:
                os.remove(source_file)
                print("The core.c file in the installation directory has been deleted")
            except Exception as e:
                print(f"An error occurred while deleting core.c: {e}")


extensions = [
    Extension(
        "pygray_snap.core",
        ["pygray_snap/core.c"],
    )
]

setup(
    name="pygray_snap",
    version="0.1",
    author="Smawe",
    author_email="1281722462@qq.com",
    packages=find_packages(exclude=('test*',)),
    ext_modules=extensions,
    package_data={"pygray_snap": ["*.wasm", "ua.jsonl", "*.pyi"]},
    exclude_package_data={"pygray_snap": ["*.pyx"]},
    include_package_data=True,
    install_requires=['pyevaljs3 >= 0.2.0', 'pytz', 'pycryptodome'],
    cmdclass={"install": CustomInstall}
)
