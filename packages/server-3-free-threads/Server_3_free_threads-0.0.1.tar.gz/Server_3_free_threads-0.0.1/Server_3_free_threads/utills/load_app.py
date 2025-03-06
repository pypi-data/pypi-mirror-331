import os
import logging
import pathlib
import sys
from sysconfig import get_paths
import subprocess
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)


def load_app(path_app):
    dir_app = path_app.split('.')[0]
    path_site_packages = pathlib.Path(get_paths()['platlib'])
    abs_path = pathlib.Path(os.getcwd())
    abs_path_app = abs_path.joinpath(dir_app)

    dir_app_path_site_packages = path_site_packages.joinpath(dir_app)
    if dir_app_path_site_packages.exists():
        result = subprocess.run(args=('rm', '-r', dir_app_path_site_packages))
    if abs_path_app.exists() and path_site_packages.exists():
        log.info("пути к пакетам python и приложению wsgi существуют")
        result = subprocess.run(args=('cp', '-r', abs_path_app, path_site_packages))
        if result.returncode == 0:
            return True
        else:
            return False
