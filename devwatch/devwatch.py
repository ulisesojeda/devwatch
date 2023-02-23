""" devwatch """

import argparse
import glob
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from ctypes import CDLL, c_int, get_errno
from ctypes.util import find_library
from errno import EINTR
from fcntl import ioctl
from pathlib import Path
from select import poll
from struct import calcsize, unpack
from termios import FIONREAD

import yaml

CONF_NAME = ".devwatchrc.yml"
libc_so = find_library("c")
libc = CDLL(libc_so or "libc.so.6", use_errno=True)
EVENT_FMT = "iIII"
EVENT_SIZE = calcsize(EVENT_FMT)
IN_MODIFY = 0x00000002


def load_config(target):
    """Load configuration"""
    local = Path.joinpath(Path.cwd(), CONF_NAME)
    home = Path.joinpath(Path.home(), CONF_NAME)

    if local.exists():
        conf_file = local
    elif home.exists():
        conf_file = home
    else:
        print(
            f"Error: missing {CONF_NAME}. "
            f"Create file {CONF_NAME} on home or working directory"
        )
        sys.exit(1)

    with open(conf_file, "r", encoding="utf-8") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if target and target not in cfg:
        print(f"Error: invalid target: {target}")
        sys.exit(1)

    if not target:  # Get first target as default
        if len(cfg.keys()) > 0:
            target = list(cfg.keys())[0]
        else:
            print(f"Error: empty {CONF_NAME} files.")
            sys.exit(1)

    if "files" not in cfg[target]:
        print("Error: missing `files` entry for target: {target}")
        sys.exit(1)
    if "command" not in cfg[target]:
        print("Error: missing `command` entry for target: {target}")
        sys.exit(1)

    files = glob.glob(cfg[target]["files"], recursive=True)
    dirs = list(set([os.path.dirname(file) for file in files]))
    command = cfg[target]["command"]
    return dirs, files, command


def libc_call(function, *args):
    """Wrapper which raises errors and retries on EINTR."""
    while True:
        rc = function(*args)
        if rc != -1:
            return rc
        errno = get_errno()
        print(f"ERRNO: {errno}")
        if errno != EINTR:
            print(f"ERRNO: {errno}")
            raise OSError(errno, os.strerror(errno))


def read_all(fd):
    """Read all available data from file description"""
    bytes_avail = c_int()
    ioctl(fd, FIONREAD, bytes_avail)
    if not bytes_avail.value:
        data = b""
    else:
        data = os.read(fd, bytes_avail.value)
    return data


def target(dir, files, command):
    try:
        fd = libc_call(libc.inotify_init)
        poller = poll()
        poller.register(fd)

        encoded_path = dir.encode("utf-8")
        libc_call(libc.inotify_add_watch, fd, encoded_path, IN_MODIFY)

        while True:
            data = None
            if poller.poll(None):
                data = read_all(fd)
            if data:
                # Unpack the first 4 bytes to get namesize
                _, _, _, namesize = unpack(EVENT_FMT, data[:EVENT_SIZE])
                ini_pos = EVENT_SIZE
                end_pos = EVENT_SIZE + namesize
                name = data[ini_pos:end_pos].split(b"\x00", 1)[0]
                name = name.decode("utf-8")

                if name:
                    file_path = str(os.path.join(dir, name))
                    if file_path in files:
                        execute = (
                            command.replace("@", file_path) if "@" in command else command
                        )
                        subprocess.run("clear", shell=True, check=False)
                        subprocess.run(execute, shell=True, check=False)

                        libc_call(libc.inotify_add_watch, fd, encoded_path, IN_MODIFY)
    except Exception as exc:
        print(exc)


def _start(dirs, files, command):
    MAX_DIRS = 100
    _dirs = dirs[:MAX_DIRS]
    workers = len(_dirs)

    with ThreadPoolExecutor(max_workers=workers + 1) as executor:
        [executor.submit(target, dir, files, command) for dir in _dirs]


def main(target):
    """Main function"""
    dirs, files, command = load_config(target)

    if not files:
        print(
            f"Error: invalid target: {target}."
            f"Path not found: {files}. Check {CONF_NAME}"
        )
        sys.exit(1)

    _start(dirs, files, command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target")
    argv = parser.parse_args()
    main(argv.target)
