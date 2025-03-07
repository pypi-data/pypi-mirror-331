import os
import pathlib
import shutil
from setuptools import setup

version = open('version').read().strip()
requirements = open('requirements.txt').read().split()
__cur_path = pathlib.Path(__file__).parent.resolve()
shutil.copyfile(f"{__cur_path}{os.sep}version", f"{__cur_path}{os.sep}malevich_app{os.sep}version")


setup(
    name='malevich_app',
    version=version,
    author="Andrew Pogrebnoj",
    author_email="andrew@malevich.ai",
    package_dir={"malevich_app": "malevich_app"},   # FIXME
    package_data={"": ["version"]},
    install_requires=requirements,
)
