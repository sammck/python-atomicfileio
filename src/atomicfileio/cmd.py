#!/usr/bin/env python3

from typing import ( BinaryIO, List, Optional )
from atomicfileio import atomic_open

import sys
import argparse
from pwd import getpwnam
from grp import getgrnam

BUFFER_SIZE: int = 1024*1024

def _copy_from_infd(
      infd: BinaryIO,
      output_file: str,
      force_permissions: bool,
      user: Optional[str],
      group: Optional[str],
      perms: Optional[int],
      effective_umask: Optional[int],
      keep_temp_file: bool=False,
    ):
  with atomic_open(
        output_file,
        mode='wb',
        replace_perms=force_permissions,
        uid=user,
        gid=group,
        perms=perms,
        effective_umask=effective_umask,
        keep_temp_file_on_error=keep_temp_file
      ) as fd:
    fd: BinaryIO
    while True:
      buffer = infd.read(BUFFER_SIZE)
      if len(buffer) == 0:
        break
      fd.write(buffer)


def run(argv: List[str]) -> int:
  parser = argparse.ArgumentParser(description="Atomically replace the contents of a file")

  parser.add_argument("output_file", help="File to update atomically")

  parser.add_argument("-i", "--input-file", default=None, help="Read from named file. By default, stdin is read.")
  parser.add_argument("-f", "--force-permissions", default=False, action='store_true', help="Replace file owner, group, and permission mode bits even if file alread exists. By default, existing permissions are retained.")
  parser.add_argument("-u", "--user", default=None, help="The owning user name or UID number if file does not exist or --force-permissions is used. If not provided, the default owner is used.")
  parser.add_argument("-g", "--group", default=None, help="The owning group name or GID number if file does not exist or --force-permissions is used. If not provided, the default group is used.")
  parser.add_argument("-p", "--perms", default=None, help="The permission mode bits (in octal) if file does not exist or --force-permissions is used. If not provided, the default permission bits allowed by umask is used.")
  parser.add_argument("--umask", default=None, help="The umask value (in octal) to use if the file does not exist or --force-permisions is used. If not provided, the current process umask value is used.")
  parser.add_argument("-k", "--keep-temp-file", default=False, action='store_true', help="Keep temp file on error. By default, a best effort is made to delete the temp file if unsuccessful.")

  
  args = parser.parse_args(argv)

  output_file: str = args.output_file
  force_permissions: bool = args.force_permissions
  input_file: Optional[str] = args.input_file
  user_str: Optional[str] = args.user
  group_str: Optional[str] = args.group
  perms_str: Optional[str] = args.perms
  mask_str: Optional[str] = args.umask
  keep_temp_file: bool = args.keep_temp_file

  perms: Optional[int] = None
  mask: Optional[int] = None

  if not perms_str is None:
    perms = int(perms_str, 8)

  if not mask_str is None:
    mask = int(mask_str, 8)

  if input_file is None:
    infd = sys.stdin.buffer
    _copy_from_infd(
        infd,
        output_file=output_file,
        force_permissions=force_permissions,
        user=user_str,
        group=group_str,
        perms=perms,
        effective_umask=mask,
        keep_temp_file=keep_temp_file
      )
  else:
    with open(input_file, 'rb') as infd:
      infd: BinaryIO
      _copy_from_infd(
          infd,
          output_file=output_file,
          force_permissions=force_permissions,
          user=user_str,
          group=group_str,
          perms=perms,
          effective_umask=mask,
          keep_temp_file=keep_temp_file
        )
  return 0

def main():
  exit_code = run(sys.argv[1:])
  sys.exit(exit_code)

if __name__ == '__main__':
  main()
