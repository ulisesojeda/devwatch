""" devwatch """

import argparse
import os
import subprocess
from ctypes import CDLL, c_int, get_errno
from ctypes.util import find_library
from errno import EINTR
from fcntl import ioctl
from pathlib import Path
from select import poll
from struct import calcsize, unpack
import sys
from termios import FIONREAD

import yaml


def load_config(target):
  """Load configuration"""
  conf_name = ".devwatchrc.yml"
  local = Path.joinpath(Path.cwd(), conf_name)
  home = Path.joinpath(Path.home(), conf_name)

  if local.exists():
    conf_file = local
  elif home.exists():
    conf_file = home
  else:
    print(f"Error: missing {conf_name}. Create file {conf_name} on home or working directory")
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
        print(f"Error: empty {conf_name} files.")
        sys.exit(1)

  if "files" not in cfg[target]:
    print("Error: missing `files` entry for target: {target}")
    sys.exit(1)
  if "command" not in cfg[target]:
    print("Error: missing `command` entry for target: {target}")
    sys.exit(1)

  files = cfg[target]["files"]
  command = cfg[target]["command"]
  return files, command


def libc_call(function, *args):
  """Wrapper which raises errors and retries on EINTR."""
  while True:
    rc = function(*args)
    if rc != -1:
      return rc
    errno = get_errno()
    print(f"ERRNO: {errno}")
    if errno != EINTR:
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


def main(target):
  """Main function"""
  files, command = load_config(target)

  if not os.path.exists(files):
    print(
        f"Error: invalid target: {target}."
        f"Path not found: {files}. Check {conf_name}"
    )
    sys.exit(1)

  libc_so = find_library("c")
  libc = CDLL(libc_so or "libc.so.6", use_errno=True)

  fd = libc_call(libc.inotify_init)

  poller = poll()
  poller.register(fd)

  encoded_path = files.encode("utf-8")
  IN_MODIFY = 0x00000002
  libc_call(libc.inotify_add_watch, fd, encoded_path, IN_MODIFY)

  EVENT_FMT = "iIII"
  EVENT_SIZE = calcsize(EVENT_FMT)

  while True:
    if poller.poll(None):
      data = read_all(fd)
    if data:
      # Unpack the first 4 bytes to get namesize
      _, _, _, namesize = unpack(EVENT_FMT, data[:EVENT_SIZE])
      ini_pos = EVENT_SIZE
      end_pos = EVENT_SIZE + namesize
      name = data[ini_pos:end_pos].split(b"\x00", 1)[0]
      name = name.decode("utf-8")

      if os.path.isdir(files):
         parameters = str(os.path.join(files, name))
         if "@" in command:
            command = command.replace("@", parameters)
      else:
         parameters = files

      subprocess.run("clear", shell=True, check=False)
      subprocess.run(command, shell=True, check=False)

      libc_call(libc.inotify_add_watch, fd, encoded_path, IN_MODIFY)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--target")
  argv = parser.parse_args()
  main(argv.target)
