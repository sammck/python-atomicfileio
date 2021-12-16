
import datetime
import typing as t
from dateutil.parser import isoparse as dateutil_isoparse, parse as dateutil_parse
from nr.parsing.date import format_set, ISO_8601
from test.samples import SAMPLES

STDLIB_ISO_8601_DATETIME_FORMATS = [
  '%Y-%m-%dT%H:%M:%S.%f%z',
  '%Y-%m-%dT%H:%M:%S.%f',
  '%Y-%m-%dT%H:%M:%S%z',
  '%Y-%m-%dT%H:%M:%S',
  '%Y%m%dT%H%M%S%z',
  '%Y%m%dT%H%M%S',
  '%Y%m%d',
]

STDLIB_ISO_8601_DATETIME_FORMATS_REVERSED = list(reversed(STDLIB_ISO_8601_DATETIME_FORMATS))

ISO8601_DATETIME_SAMPLES = SAMPLES[SAMPLES.tags.apply(lambda x: 'iso8601' in x) &
  SAMPLES.parsed.apply(lambda x: isinstance(x, datetime.datetime))]


def vectorize(func, *args):
  for _idx, row in ISO8601_DATETIME_SAMPLES.iterrows():
    func(row.formatted, row.parsed, *args)


def parse_datetime_stdlib(s: str, expected: datetime.datetime, formats: t.List[str]) -> None:
  for fmt in formats:
    try:
      parsed = datetime.datetime.strptime(s, fmt)
      break
    except ValueError:
      pass
  else:
    raise ValueError(f'Unable to parse {s!r} using {formats!r}')
  assert parsed == expected


def parse_datetime_nr(s: str, expected: datetime.datetime, format: format_set) -> None:
  parsed = format.parse_datetime(s, True)
  assert parsed == expected


def parse_dateutil_parse(s: str, expected: datetime.datetime) -> None:
  parsed = dateutil_parse(s)
  assert parsed == expected


def parse_dateutil_isoparse(s: str, expected: datetime.datetime) -> None:
  parsed = dateutil_isoparse(s)
  assert parsed == expected


class DatetimeParsingSuite:
  """
  An example benchmark that times the performance of various kinds
  of iterating over dictionaries in Python.
  """

  def time_datetime_datetime_strptime(self):
    vectorize(parse_datetime_stdlib, STDLIB_ISO_8601_DATETIME_FORMATS)

  def time_datetime_datetime_strptime_reversed(self):
    vectorize(parse_datetime_stdlib, STDLIB_ISO_8601_DATETIME_FORMATS)

  def time_nr_parsing_date_ISO_8601_parse_datetime(self):
    vectorize(parse_datetime_nr, ISO_8601)

  def time_dateutil_parser_parse(self):
    vectorize(parse_dateutil_parse)

  def time_dateutil_parser_isoparse(self):
    vectorize(parse_dateutil_isoparse)
