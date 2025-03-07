import os
import pwd
import subprocess
from functools import lru_cache


@lru_cache()
def get_shell():
    shell = os.environ.get("SHELL")
    if shell:
        return shell
    return pwd.getpwuid(os.getuid()).pw_shell


@lru_cache()
def get_mac_version():
    return subprocess.check_output(["sw_vers", "-productVersion"]).decode("utf-8").strip()
