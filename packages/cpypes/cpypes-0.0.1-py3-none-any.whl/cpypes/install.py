import appdirs
import importlib.metadata
import importlib.resources
import gzip
import os
import shutil
import subprocess
import sys
import tarfile

from . import data

NO_ACTION_NEEDED = 0
ACTION_COMPLETED = 1

def install():
    this_version = _get_package_version()
    if _get_installed_server_version(install_path) == this_version:
        return NO_ACTION_NEEDED

    uninstall()

    os.makedirs(install_path)
    data_resource = importlib.resources.files(data)
    with data_resource.joinpath("server.tar.gz").open("rb") as f:
        with gzip.GzipFile(fileobj=f) as gf:
            with tarfile.TarFile(fileobj=gf) as tf:
                tf.extractall(install_path)

    _compile_server(os.path.join(install_path, "server"))

    with open(os.path.join(install_path, "version"), "w") as f:
        f.write(_get_package_version() + "\n")

    return ACTION_COMPLETED

def uninstall():
    try:
        shutil.rmtree(install_path)
    except FileNotFoundError:
        return NO_ACTION_NEEDED
    return ACTION_COMPLETED


def _compile_server(server_dir):
    try:
        sp = subprocess.run(["make", "-C", server_dir],
            capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("[-] Failed to compile cpypes server")
        print(f"[-] Return code {e.returncode}")
        print("[-] Note: Compilation requires at least: make, gcc,",
            "libffi-dev")
        print("[-] stdout from `make`:")
        print("=" * 70)
        print(e.stdout)
        print("=" * 70)
        print("[-] stderr from `make`:")
        print("=" * 70)
        print(e.stderr)
        print("=" * 70)
        raise e

def _get_installed_server_version(install_dir):
    if not os.path.isdir(install_dir):
        return None
    try:
        with open(os.path.join(install_dir, "version")) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def _get_install_path():
    this_package = _get_package_name()
    if sys.base_prefix != sys.prefix:
        # We're in a .venv
        return os.path.join(sys.prefix, this_package)
    else:
        # System-wide Python.
        return appdirs.user_data_dir(this_package)

def _get_package_name():
    return __name__.split(".")[0]

def _get_package_version():
    return importlib.metadata.version(_get_package_name())


install_path = _get_install_path()
server_path = os.path.join(install_path, "server", "main")
