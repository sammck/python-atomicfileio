"""Support for safely atomically updating files

This module provides tools for overwriting files in such a way that a reader will never see a partially written file.

Portions borrowed from https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/,
also under the MIT license.
"""
__version__ = "1.0.1"

from typing import Optional, Union, TextIO, BinaryIO, ContextManager
import os
import sys
import stat
import sys
import tempfile
import contextlib
import subprocess
from pwd import getpwnam
from grp import getgrnam

# Import os.replace if possible; otherwise emulate it as well as possible
try:
  from os import replace  # Python 3.3 and better.
except ImportError:
  if sys.platform == 'win32':
    # This is definitely not atomic!
    # But it's how (for example) Mercurial does it, as of 2016-03-23
    # https://selenic.com/repo/hg/file/tip/mercurial/windows.py
    def replace(source, destination):
      assert sys.platform == 'win32' 
      try:
        os.rename(source, dest)
      except OSError as err:
        if err.winerr != 183:
          raise
        os.remove(dest)
        os.rename(source, dest)
  else:
    # Atomic on POSIX. Not sure about Cygwin, OS/2 or others.
    from os import rename as replace


def current_umask(thread_safe: bool=True) -> int:
  """Makes a best attempt to determine the current umask value of the calling process in a safe way.

  Unfortunately, os.umask() is not threadsafe and poses a security risk, since there is no way to read
  the current umask without temporarily setting it to a new value, then restoring it, which will affect
  permissions on files created by other threads in this process during the time the umask is changed, or
  by any child processses that were forked during this time.

  On recent linux kernels (>= 4.1), the current umask can be read from /proc/self/status.

  On older systems, the simplest safe way is to spawn a shell and execute the 'umask' command. The shell will
  inherit the current process's umask, and will use the unsafe call, but it does so in a separate,
  single-threaded process, which makes it safe.

  Args:
    thread_safe:  If False, allows the current umask to be determined in a potentially unsafe, but more
                    efficient way. Should only be set to False if the caller can guarantee that there
                    are no other threads running in the current process that might read or set the umask,
                    create files, or spawn child processes. Default is True.

  Returns:
    int: The current process's umask value
  """
  if not thread_safe:
    mask = os.umask(0o066)   # 0o066 is arbitrary but poses the least security risk if there is a race.
    # WARNING: At this point, and other threads that create files, or spawn subprocesses that create files,
    # will be using an incorrect umask of 0o066, which denies all access to anyone but the owner.
    os.umask(mask)
  else:
    mask: Optional[int] = None
    try:
      with open('/proc/self/status') as fd:
        for line in fd:
          if line.startswith('Umask:'):
            mask = int(line[6:].strip(), 8)
            break
    except FileNotFoundError:
      pass
    except ValueError:
      pass
    if mask is None:
      # As a last resort, do the dangerous call under a forked, single-threaded subprocess.
      mask = int(subprocess.check_output('umask', shell=True).decode('utf-8').strip(), 8)
  return mask

def normalize_uid(uid: Optional[Union[int, str]]) -> Optional[int]:
  """
  Normalizes a posix user ID that may be expressed as:
     1. An integer UID
     2. A string containing a decimal UID
     3. A string containing a valid posix username
     4. None, which causes None to be returned

  Args:
    uid: An integer UID, a decimal string UID, a posix username, or None.

  Returns:
    Optional[int]: The integer UID corresponding to `uid`, or None if `uid` is None

  Raises:
    KeyError: A nondecimal string was provided and the posix username does not exist
  """
  if not uid is None:
    try:
      uid = int(uid)
      return uid
    except ValueError:
      uid = getpwnam(uid).pw_uid
  return uid

def normalize_gid(gid: Optional[Union[int, str]]) -> Optional[int]:
  """
  Normalizes a posix group ID that may be expressed as:
     1. An integer GID
     2. A string containing a decimal GID
     3. A string containing a valid posix group name
     4. None, which causes None to be returned

  Args:
    gid: An integer GID, a decimal string GID, a poxix group name, or None.

  Returns:
    Optional[int]: The integer GID corresponding to `gid`, or None if `gid` is None

  Raises:
    KeyError: A nondecimal string was provided and the posix group name does not exist
  """
  if not gid is None:
    try:
      gid = int(gid)
      return gid
    except ValueError:
      gid = getgrnam(gid).gr_gid
  return gid



@contextlib.contextmanager
def atomic_open(
      filename: str,
      mode: str='w',
      replace_perms: bool=False,
      effective_umask: Optional[int]=None,
      uid: Optional[Union[int, str]]=None,
      gid: Optional[Union[int, str]]=None,
      perms: Optional[int]=None,
      temp_file_base_name: Optional[str]=None,
      temp_file_suffix: str='.tmp',
      keep_temp_file_on_error: bool=False,
      buffering: int=-1,
      encoding: Optional[str]=None,
      errors: Optional[str]=None,
      newline: Optional[str]=None,

    ) -> ContextManager[Union[TextIO, BinaryIO]]:
  """Open a file for atomic create or overwrite, using a temporary file managed by a context.

  Args:
    filename:                 The final filename to create or overwrite.
    mode:                     The open mode, as defined for `open()`. Only 'w' and 'wb' are allowed. Default is 'w'.
    replace_perms:            True if the file's UID, GID, and perms should be replaced even
                                if the file already exists. Default is False.
    effective_umask:          Optionally, a umask value to use for creation of a new file. If None, the current process's umask is
                                use. If 0, none of the bits in `perms`will be masked. Any bits set to 1 will be masked off in the
                                final file permissions if a new file is created. Ignored if `replace_perms` is False and a file
                                already exists. Default is None.
    uid:                      If the file does not exist or `replace_perms` is True, the owner UID to use for the
                                new file, or None to use the default UID. For convenience, a string containing the decimal UID or a
                                username may be provided. Ignored if the file exists and `replace_perms`
                                is False. Default is None.
    gid:                      If the file does not exist or `replace_perms` is True, the group GID to use for the
                                new file, or None to use the default GID.  For convenience, a string containing the decimal GID or
                                a group name may be provided. Ignored if the file exists and `replace_perms`
                                is False. Default is None.
    perms:                     If the file does not exist or `replace_perms` is True, the permission mode bits to use for the
                                new file, or None to use the default mode bits (typically 0o664).  Ignored if the file exists
                                and `replace_perms` is False. Default is None.
    temp_file_base_name:      The name to use for the temporary file (after a '.', a random string, and `temp_file_suffix` is appended), or
                                None to use `filename` as the base name. Default is None.
    temp_file_suffix:         A string to put at the end of the temp file name.  Defaults to '.tmp'
    keep_temp_file_on_error:  True if the temporary file should be retained if a failure occurs before
                                it is fully written and atomically moved to the final `filename`. Default
                                is False
    buffering:                As defined for open()
    encoding:                 As defined for open()
    errors:                   How to handle encoding errors, as defined for open()
    newline:                  As defined for open()

  Returns:
    A `ContextManager` that will provide an open, writeable stream to a temporary file. On context exit without any exception raised,
    the temporary file will be renamed to atomically replace any previous file.

  Example:

    Update the linux hostname file atomically (must be run as root):

    ```
    with atomic_open("/etc/hostname", 'w', perms=0o644) as f:
      f.write("myhostname")
    ```

  The behavior of this function mimics `open(filename, 'w')` as nearly as possible, except that
  the target file will appear, to readers, to be atomically replaced at with-block exit time, and update
  will be cancelled if an exception is raised within the with-block.

  The context manager opens a temporary file for writing in the same
  directory as `filename`. On cleanly exiting the with-block, the temporary
  file is renamed to the given filename. If the original file already
  exists, it will be overwritten and any existing contents replaced.
  On POSIX systems, the rename is atomic. Other operating systems may
  not support atomic renames, in which case a best effort is made.

  The temporary file will be created in the same directory as `filename`, and will
  have the name `f"{base_name}.{random_8_chars}{temp_file_suffix}"`, where
  `base_name` is `temp_file_base_name` if provided, or `filename` otherwise.
  `random_8_chars` is a random 8-character string as generated by `tempfile.mkstemp()`.

  The temporary file naturally ceases to exists with successful
  completion of the with-block. If an uncaught exception occurs inside the with-block,
  the original file is left untouched. If `keep_temp_file_on_error`
  is True, the temporary file is also preserved, for diagnosis or data
  recovery. If False (the default), the temporary file is deleted on any catchable
  exception. In this case, any errors in deleting the temporary file are ignored.
  Of course, uncatchable exceptions or system failures may result
  in a leaked temporary file; it is the caller's responsibility to
  periodically clean up orphaned temporary files.

  By default, the temporary file is opened in text mode. To use binary mode,
  pass `mode='wb'` as an argument. On some operating systems, this makes
  no difference.

  Applications that use this function generally will want to set the final value
  of UID, GID, and permissions mode bits on the temporary file before it is renamed
  to the target filename. For this reason, additional optional arguments can be included
  to make this simple and seamless. If these arguments are omitted, the UID, GID, and
  permission mode bits of the target file will be as defined for `open()`.

  If `filename` exists and `replace_perms` is False, then the existing UID, GID,
  and permission mode bits of `filename` will be applied to the
  temporary file before it is written, and preserved when the temporary
  file replaces the original. If `filename` does not exist, or `replace_perms`
  is True, then `uid`, `gid`, and `perms` are used--if one or more of
  these is None, then defaults are used as with open(). Note that in the case of
  the perms bits, the defaults are as constrained by the current umask or parameter
  `effective_umask`--this is different than tempfile.mkstemp() which limits
  permissions to 0o600, but is consistent with the behavior of `open()`.
  In any case, the final UID, GID, and permissions mode bits have already been
  set appropriately on entry to the with-block, so the caller is free to make
  further adjustments to them before exiting the with-block, and their adjustments
  will not be overwritten.
  """

  if not mode in ['w', 'wt', 'wb']:
    raise ValueError(f"atomic_open() does not support open mode \"{mode}\"")

  is_text = mode != 'wb'

  if temp_file_base_name is None:
    temp_file_base_name = filename

  pathname = os.path.realpath(filename)
  uid = normalize_uid(uid)
  gid = normalize_gid(gid)

  if not replace_perms:
    try:
      st = os.stat(pathname)
      uid = st.st_uid
      gid = st.st_gid
      perms = stat.S_IMODE(st.st_mode)
      # since we are using an existing file's perms, we never want to mask off permission bits.
      effective_umask = 0
    except FileNotFoundError:
      pass

  if perms is None:
     perms = 0o666   # By default, newly created files will get all permissions (except execute) not excluded by umask
  if effective_umask is None:
    effective_umask = current_umask()
  perms = perms & (~effective_umask)

  dirpath = os.path.dirname(pathname)
  fd: Optional[int] = None
  temp_pathname: Optional[str] = None
  need_close = True
  need_delete = not keep_temp_file_on_error
  fd, temp_pathname = tempfile.mkstemp(suffix=temp_file_suffix, prefix=temp_file_base_name + '.', dir=dirpath, text=is_text)
  # Note that at this point the temporary file is owned by the calling user, with permission bits 600 as defined by `mkstemp`.
  # This is different than the default behavior for open() which uses default umask permissions, typically 664 for users and
  # 644 for root. Since we want to mimic open(), we will need to compensate for that.
  try:
    fctx = os.fdopen(fd, mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)
    need_close = False  # fd is now owned by fctx and will be closed on exit from the with block
    with fctx as f:
      # We update the owner, group, and permission mode bits before returning the context manager; this allows
      # the caller to make additional changes to these properties if desired before exiting the context. To avoid potential
      # permission errors, only make changes if they are necessary.
      st = os.stat(fd)
      current_perms = stat.S_IMODE(st.st_mode)
      current_uid = st.st_uid
      current_gid = st.st_gid
      if not (uid is None or uid == current_uid) or not (gid is None or gid == current_gid):
        os.fchown(fd, uid=(-1 if (uid is None or uid == current_uid) else uid), gid=(-1 if (gid is None or gid == current_gid) else gid))
      if perms != current_perms:
        os.fchmod(fd, perms)

      yield f   # return context manager to the caller, and wait until the context is closed

      # At this point the context returned to the caller has been closed

    # If we get here, the caller has cleanly closed the context without raising an exception, and the temporary file is complete and closed.
    # Perform an atomic rename (if possible). This will be atomic on POSIX systems, and Windows for Python 3.3 or higher.
    replace(temp_pathname, pathname)

    # The rename was successful, so there is no need to try to delete the temporary file.
    need_delete = False
  finally:
    try:
      if need_close:
        os.close(fd)
    finally:
      if need_delete:
        # Silently delete the temporary file. Suppress any errors (original exceptions will propagate), while passing signals, etc.
        try:
          os.unlink(temp_pathname)
        except Exception:
          pass
