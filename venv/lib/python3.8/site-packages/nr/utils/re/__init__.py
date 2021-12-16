# -*- coding: utf8 -*-
# Copyright (c) 2020 Niklas Rosenstein
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
Utility functions for regular expressions. Builds on top of the standard library #re module.
"""

from __future__ import absolute_import
import re
import typing as t

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.3.1'


class MatchAllError(ValueError):
  """
  Raised when #match_all() cannot consume the full string.
  """

  def __init__(self, regex: 're.Pattern', string: str, endpos: int) -> None:
    self.regex = regex
    self.string = string
    self.endpos = endpos

  def __str__(self):
    return 'could not consume whole string with regex {} (got until position {})'.format(
      self.regex, self.endpos)


def match_all(expr: t.Union[str, 're.Pattern'], string: str) -> t.Iterable['re.Match']:
  """
  Matches *expr* from the start of *string* and expects that it can be matched throughout.
  If it fails to consume the full string, a #MatchAllError will be raised. (Note that this
  exception class is also accessible as #match_all.Error).
  """

  if isinstance(expr, str):
    expr = re.compile(expr)

  offset = 0
  while offset < len(string):
    match = expr.match(string, offset)
    if not match:
      raise MatchAllError(expr, string, offset)
    offset = match.end()
    yield match
