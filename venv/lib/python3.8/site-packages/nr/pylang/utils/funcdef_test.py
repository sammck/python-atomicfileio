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

from nr.pylang.utils.funcdef import copy_function, raise_kwargs
import pytest


def test_raise_kwargs():

  def my_function(**kwargs):
    raise_kwargs(kwargs)

  with pytest.raises(TypeError) as excinfo:
    my_function(a=42)

  assert str(excinfo.value) == "'a' is an invalid keyword argument for my_function()"


class ClosureNotReplaced(Exception):
  pass


def create_function_with_closure(value, expected_value):
  def check():
    if value != expected_value:
      raise ClosureNotReplaced
  return check


def test_has_closure():
  func = create_function_with_closure('bar', 'foo')
  assert len(func.__closure__) == 2
  with pytest.raises(ClosureNotReplaced):
    func()

  func = copy_function(func, closure={'value': 'foo'})
  func()


def test_copy_function():
  def test(value):
    def x():
      return value
    return x
  x = test(42)
  assert x() == 42
  y = copy_function(x, closure={'value': 99})
  assert y() == 99
