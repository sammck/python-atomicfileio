# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

__all__ = ['atomic_file']

from ._tempfile import tempfile
from ._path import base, dir, isfile, join, remove, rename

import io
import shutil


class atomic_file(object):
  """
  A context-manager for creating a new temporary file that will then replace
  an existing file atomatically. This class has to be used as a
  context-manager.
  """

  @classmethod
  def dispatch(cls, filename, mode, encoding=None):
    if 'r' in mode or 'a' in mode:
      return io.open(filename, mode, encoding=encoding)
    elif 'w' in mode:
      return cls(filename, 'b' not in mode, encoding=None)

  def __init__(self, filename, text=False, encoding=None, temp_dir=None):
    self._filename = filename
    self._tempfile = tempfile(base(filename), 'atomic',
      dir=temp_dir, text=text, encoding=encoding)
    self._discard = False

  def __enter__(self):
    self._tempfile.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    try:
      if exc_type is None:
        self._replace()
    finally:
      self._tempfile.__exit__(exc_type, exc_value, exc_tb)

  def __getattr__(self, name):
    return getattr(self._tempfile, name)

  def _replace(self):
    if self._discard:
      return
    if not self._tempfile.closed:
      self._tempfile.close()

    delete_file = None
    if isfile(self._filename):
      delete_file = join(dir(self._filename), '~.' + base(self._filename))
      rename(self._filename, delete_file)

    shutil.move(self._tempfile.name, self._filename)

    if delete_file:
      remove(delete_file)

  def discard(self):
    self._discard = True
