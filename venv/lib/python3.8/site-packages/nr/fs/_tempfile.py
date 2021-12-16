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

"""
A better temporary file class.
"""

__all__ = ['tempfile', 'tempdir']

import codecs
import errno
import io
import os
import shutil
import tempfile as _tempfile


class tempfile(object):
  """
  A proper named temporary file that is only deleted when the context-manager
  exits, not when the file is closed. Note that the file is also only opened
  via the context-manager.
  """

  def __init__(self, suffix='', prefix='tmp', dir=None, text=False, encoding=None):
    self._text = text
    self._encoding = encoding
    self._mktemp = lambda: _tempfile.mkstemp(suffix, prefix, dir, text)
    self._fp = None
    self._name = None

  def __repr__(self):
    return '<tempfile name={!r}>'.format(self._name)

  @property
  def name(self):
    return self._name

  def __enter__(self):
    fd, self._name = self._mktemp()
    self._fp = os.fdopen(fd, 'w' if (self._text and not self._encoding) else 'wb')
    if self._encoding:
      self._fp = codecs.getwriter(self._encoding)(self._fp)
    if self._text and not self._encoding:
      self._encoding = self._fp.encoding
    return self

  def __exit__(self, *args):
    self._fp.close()
    try:
      os.remove(self._name)
    except OSError as e:
      if e.errno != errno.ENOENT:
        raise

  @property
  def encoding(self):
    return self._encoding

  def writable(self):
    return True

  def write(self, data):
    return self._fp.write(data)

  @property
  def closed(self):
    return self._fp.closed

  def close(self):
    self._fp.close()

  def tell(self):
    return self._fp.tell()

  def seekable(self):
    return False

  def readable(self):
    return False


class tempdir(object):
  """
  A context manager for a temporary directory.
  """

  def __init__(self, suffix='', prefix='', dir=None):
    self._mkdtemp = lambda: _tempfile.mkdtemp(suffix, prefix, dir)
    self._name = None

  def __repr__(self):
    return '<tempdir name={!r}>'.format(self._name)

  def __enter__(self):
    self._name = self._mkdtemp()
    return self

  def __exit__(self, *args):
    self.close()

  @property
  def name(self):
    return self._name

  def close(self):
    if not self._name:
      return
    try:
      shutil.rmtree(self._name)
    except OSError as e:
      if e.errno != errno.ENOENT:
        raise

  def open(self, path, *args, **kwargs):
    return io.open(os.path.join(self._name, path), *args, **kwargs)
