import platform
import sys


def get_os_and_arch():
    os_name = "Unknown"
    arch = "Unknown"

    if sys.platform.startswith("darwin"):
        os_name = "macOS"
    elif sys.platform.startswith("win"):
        os_name = "Windows"
    elif sys.platform.startswith("linux"):
        os_name = "Linux"

    machine = platform.machine().lower()
    if machine == "x86_64" or machine == "amd64":
        arch = "x86_64"
    elif machine.startswith("arm") or machine.startswith("aarch"):
        arch = "ARM64"
    elif machine == "i386":
        arch = "x86"

    return os_name, arch
