import argparse

from . import install

parser = argparse.ArgumentParser(prog="cpypes",
    description="cpypes server installation helper")
parser.add_argument("--install", action="store_true",
    help="Install the cpypes server")
parser.add_argument("--uninstall", action="store_true",
    help="Uninstall the cpypes server")

args = parser.parse_args()

if args.install:
    rtn = install.install()
    if rtn == install.ACTION_COMPLETED:
        print(f"[+] Installed server in {install.install_path}")
    else:
        print(f"[+] Server already installed in {install.install_path}")

elif args.uninstall:
    rtn = install.uninstall()
    if rtn == install.ACTION_COMPLETED:
        print(f"[+] Removed server from {install.server_path}")
    else:
        print(f"[+] No server installed in {install.install_path}")

else:
    parser.print_help()
