""" devwatch """

import argparse
import glob
import os
import signal
import subprocess
import sys
from ctypes import CDLL, c_int, get_errno
from ctypes.util import find_library
from errno import EINTR
from fcntl import ioctl
from pathlib import Path
from queue import Queue, Empty
from select import poll
from struct import calcsize, unpack
from termios import FIONREAD
from threading import Thread
from itertools import chain

import yaml

CONF_NAME = ".devwatchrc.yml"
libc_so = find_library("c")
libc = CDLL(libc_so or "libc.so.6", use_errno=True)
EVENT_FMT = "iIII"
EVENT_SIZE = calcsize(EVENT_FMT)
IN_MODIFY = 0x00000002
CLOSER = Queue()
MAX_DIRS = 100
POLLER_TIMEOUT = 500
TOTAL_THREADS = 0


def glob_files(files_l):
    files_split = files_l.split(" ")
    file_list = [glob.glob(pattern, recursive=True) for pattern in files_split]
    files = list(chain(*file_list))
    dir_list = list({os.path.dirname(file) for file in files})
    dirs = [(_dir if _dir else ".") for _dir in dir_list]
    return dirs, files


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

    dirs, files = glob_files(cfg[target]["files"])
    command = cfg[target]["command"]
    return target, dirs, files, command


def libc_call(function, *args):
    """Wrapper which raises errors and retries on EINTR."""
    while True:
        ret_code = function(*args)
        if ret_code != -1:
            return ret_code
        errno = get_errno()
        print(f"ERRNO: {errno}")
        if errno != EINTR:
            print(f"ERRNO: {errno}")
            raise OSError(errno, os.strerror(errno))


def read_all(file_descriptor):
    """Read all available data from file description"""
    bytes_avail = c_int()
    ioctl(file_descriptor, FIONREAD, bytes_avail)
    if not bytes_avail.value:
        data = b""
    else:
        data = os.read(file_descriptor, bytes_avail.value)
    return data


def output(file_path, execute):
    """Print output"""
    def print_green(text):
        print(f"\033[92m {text}\033[00m")

    def print_cyan(text):
        print(f"\033[96m {text}\033[00m")

    line_1 = f"File changed: {file_path}"
    line_2 = f"Command executed: {execute}"
    box_len = max(len(line_1), len(line_2))
    print_cyan("=" * box_len)
    print_green(line_1)
    print_green(line_2)
    print_cyan("=" * box_len)
    print("")


def target_fn(directory, files, command, queue):
    """Thread target function"""
    file_descriptor = libc_call(libc.inotify_init)
    poller = poll()
    poller.register(file_descriptor)

    encoded_path = directory.encode("utf-8")
    libc_call(libc.inotify_add_watch, file_descriptor, encoded_path, IN_MODIFY)

    while True:
        data = None
        if poller.poll(POLLER_TIMEOUT):
            data = read_all(file_descriptor)

        try:
            if queue.get(block=False) == "STOP":
                break
        except Empty:
            pass

        if data:
            # Unpack the first 4 bytes to get namesize
            _, _, _, namesize = unpack(EVENT_FMT, data[:EVENT_SIZE])
            ini_pos = EVENT_SIZE
            end_pos = EVENT_SIZE + namesize
            name = data[ini_pos:end_pos].split(b"\x00", 1)[0]
            name = name.decode("utf-8")

            if name:
                file_path = str(os.path.join(directory, name))
                if file_path in files or (directory == '.' and file_path.replace("./", "") in files):
                    execute = (
                        command.replace("@", file_path)
                        if "@" in command
                        else command
                    )
                    subprocess.run("clear", shell=True, check=False)
                    output(file_path, execute)
                    subprocess.run(execute, shell=True, check=False)

                    libc_call(libc.inotify_add_watch, file_descriptor, encoded_path, IN_MODIFY)


def _start(dirs, files, command):
    global TOTAL_THREADS

    if len(dirs) > MAX_DIRS:
        raise ValueError(f"Too many directories: {len(dirs)}")

    TOTAL_THREADS = len(dirs)
    for directory in dirs:
        thread = Thread(target=target_fn, args=(directory, files, command, CLOSER))
        thread.start()


def handler(signum, frame):
    """Signal handler"""
    for _ in range(TOTAL_THREADS):
        CLOSER.put("STOP")


def main(target, files_p, command_p):
    """Main function"""
    if files_p and command_p:
        sel_target = "CUSTOM_BY_ARGS"
        dirs, files = glob_files(files_p)
        command = command_p
    else:
        sel_target, dirs, files, command = load_config(target)

    if not files:
        print(
            f"Error: Files not found for target: {sel_target}"
        )
        sys.exit(1)

    try:
        signal.signal(signal.SIGINT, handler)
    except ValueError:
        pass

    _start(dirs, files, command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target")
    parser.add_argument("-f", "--files")
    parser.add_argument("-c", "--command")
    argv = parser.parse_args()
    main(argv.target, argv.files, argv.command)
