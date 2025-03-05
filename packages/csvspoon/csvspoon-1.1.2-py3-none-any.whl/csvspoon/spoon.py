# Copyright 2019, Jean-Benoist Leger <jb@leger.tf>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import random
import math
import csv
import sys
import re
from typing import Iterator, Optional, Any, Callable, Set, Union


class CsvFileSpec:
    """A class to parse and store CSV file specifications.
    
    The specification format is: filename[:column1,column2,...] where the columns part is optional.
    
    Args:
        filespec (str): The file specification string in the format "filename[:columns]"
    
    Attributes:
        _filename (str): The CSV filename
        _columns (tuple): The column names to extract, or None if all columns should be used
    """
    
    _filename: str
    _columns: tuple[str, ...] | None
    
    def __init__(self, filespec: str) -> None:
        regex = re.compile(r"^(?P<filename>[^:]+)(?::(?P<columns>.+))?$")
        match = regex.match(filespec)
        if not match:
            raise TypeError(
                "{filespec!r} can not be interpreted as {}".format(
                    self.__class__.__name__
                )
            )
        self._filename = match["filename"]
        if match["columns"] is not None:
            self._columns = tuple(match["columns"].split(","))
        else:
            self._columns = None

    @property
    def filename(self) -> str:
        """str: Get the CSV filename"""
        return self._filename

    @property
    def columns(self) -> tuple[str, ...] | None:
        """tuple: Get the column names, or None if all columns should be used"""
        return self._columns


class CsvColumnsNotFound(Exception):
    """Exception raised when specified columns are not found in the CSV file."""
    pass


class ColFormat:
    """A class to handle column formatting.
    
    Args:
        colfmt (str): Format specification in the form "column:format" where format is a Python format string
    
    Attributes:
        _convert (callable): Function to convert the column value (int, float or identity)
        _colname (str): Name of the column to format
        _fmt (str): Python format string to apply
    """
    
    _convert: Callable[[str], int | float | str]
    _colname: str
    _fmt: str
    
    def __init__(self, colfmt: str) -> None:
        if colfmt.count(":") != 1:
            raise TypeError("Not a col format for {}".format(self.__class__.__name__))
        colname, fmt = colfmt.split(":")
        if fmt and fmt[-1] in "bcdoxXn":
            self._convert = int
        elif fmt and fmt[-1] in "eEfFgGn%":
            self._convert = float
        else:
            self._convert = lambda x: x
        self._colname = colname
        self._fmt = "{:%s}" % fmt

    def format(self, row: dict[str, str]) -> None:
        """Format a column value in the given row.
        
        Args:
            row (dict): Row containing the column to format
            
        Raises:
            CsvColumnsNotFound: If the column is not found in the row
        """
        if self._colname not in row:
            raise CsvColumnsNotFound("Column {} is not found.".format(self._colname))
        row[self._colname] = self._fmt.format(self._convert(row[self._colname]))


class NewColFormat(ColFormat):
    """A class to handle new column formatting, extending ColFormat.
    
    Allows format specification without requiring a format string.
    """
    
    def __init__(self, colfmt: str) -> None:
        if ":" not in colfmt:
            colfmt += ":"
        ColFormat.__init__(self, colfmt)

    @property
    def colname(self) -> str:
        """str: Get the column name"""
        return self._colname


class ColType:
    """A class to handle column type conversion.
    
    Args:
        coltype (str): Type specification in the form "column:type"
        
    Attributes:
        _colname (str): Name of the column
        _typename (str): Name of the type to convert to
        _type: The actual type after building the type from typename
    """
    
    _colname: str
    _typename: str
    _type: Any
    
    def __init__(self, coltype: str) -> None:
        if coltype.count(":") != 1:
            raise TypeError("Not a col type for {}".format(self.__class__.__name__))
        colname, typename = coltype.split(":")
        self._colname = colname
        self._typename = typename

    def build_type(self, glob: dict[str, Any]) -> None:
        """Build the actual type from the type name.
        
        Args:
            glob (dict): Global namespace to evaluate the type name in
        """
        self._type = eval(self._typename, glob)

    @property
    def get_coltype(self) -> tuple[str, Any]:
        """tuple: Get the column name and type as a tuple"""
        return (self._colname, self._type)


def _cast_pseudo_numerical(value: str) -> tuple[float, str]:
    """Try to extract a numerical value from the start of a string.
    
    Args:
        value (str): String to parse
        
    Returns:
        tuple: (numerical_value, remaining_string) or (inf, original_string) if no number found
    """
    for i in range(len(value), 0, -1):
        substr1, substr2 = value[0:i], value[i:]
        try:
            x = float(substr1)
        except ValueError:
            continue
        return (x, substr2)
    return (math.inf, value)


class NotValidContent(Exception):
    pass


def _cat_rowgen(
    gen1: Iterator[dict[str, str]],
    gen2: Iterator[dict[str, str]], 
    only1: set[str],
    only2: set[str]
) -> Iterator[dict[str, str]]:
    for row in gen1:
        row.update({k: "" for k in only2})
        yield row
    for row in gen2:
        row.update({k: "" for k in only1})
        yield row


def _join_rowgen(
    gen1: Iterator[dict[str, str]],
    dict_of_oth: dict[tuple[str, ...], list[dict[str, str]]],
    common: set[str],
    left_added_keys: list[str],
    added_keys: list[str],
    left: bool,
    right: bool
) -> Iterator[dict[str, str]]:
    if right:
        not_viewed_oth = set(dict_of_oth.keys())
    for l1 in gen1:
        value = tuple(l1[k] for k in common)
        if value in dict_of_oth:
            if right and value in not_viewed_oth:
                not_viewed_oth.remove(value)
            for l2 in dict_of_oth[value]:
                new_line = l1.copy()
                new_line.update(l2)
                yield new_line
        else:
            if left:
                new_line = dict(l1)
                new_line.update({k: "" for k in added_keys})
                yield new_line
    if right:
        for value in not_viewed_oth:
            for l2 in dict_of_oth[value]:
                new_line = dict(l2)
                new_line.update({k: "" for k in left_added_keys})
                yield new_line


def _aggregate_row_gen(
    new_fieldnames: list[str],
    stored_by_key_data_column: dict[tuple[Any, ...], dict[str, list[Any]]],
    aggregation: list[tuple[str, Callable[[dict[str, list[Any]]], Any]]]
) -> Iterator[dict[str, Any]]:
    fields_aggregation = set(colname for colname, _ in aggregation)
    for store in stored_by_key_data_column.values():
        row = {
            colname: store[colname][0]
            for colname in new_fieldnames
            if colname not in fields_aggregation
        }
        row.update({colname: func(store) for colname, func in aggregation})
        yield row


class ContentCsv:
    """Main class to handle CSV content with various operations.
    
    Args:
        filespec (CsvFileSpec, optional): Specification of the CSV file to read
        delim (str, optional): CSV delimiter character. Defaults to ","
        encoding (str, optional): File encoding
        _fieldnames (list, optional): Column names for internal use
        _rows (iterator, optional): Row data for internal use
        
    Attributes:
        _applied (list): List of column transformations to apply
        _types (dict): Column type conversions
        _new_fieldnames (list): Names of newly added columns
        _filters (list): Row filters to apply
        _fieldnames (list): Original column names
        _rows (iterator): Row data
        _valid (bool): Whether the content is still valid
    """
    
    _applied: list[tuple[str, Callable[[dict[str, Any]], Any]]]
    _types: dict[str, Callable[[str], Any]]
    _new_fieldnames: list[str]
    _filters: list[Callable[[dict[str, Any]], bool]]
    _fieldnames: list[str]
    _rows: Iterator[dict[str, str]]
    _valid: bool

    def __init__(
        self,
        *,
        filespec: CsvFileSpec | None = None,
        delim: str = ",",
        encoding: str | None = None,
        _fieldnames: list[str] | None = None,
        _rows: Iterator[dict[str, str]] | None = None
    ) -> None:
        self._applied = []
        self._types = {}
        self._new_fieldnames = []
        self._filters = []
        if filespec is not None:
            dialect = csv.excel
            dialect.delimiter = delim
            if filespec.filename == "-":
                f = sys.stdin
            else:
                f = open(filespec.filename, encoding=encoding)
            reader = csv.DictReader(f, dialect=dialect)
            if filespec.columns is None:
                self._fieldnames = reader.fieldnames
                fieldnames_map = {k: k for k in self._fieldnames}
            else:
                old_col_name = lambda col: col.split("=")[1] if "=" in col else col
                new_col_name = lambda col: col.split("=")[0] if "=" in col else col
                cols_not_found = set(
                    old_col_name(col) for col in filespec.columns
                ).difference(reader.fieldnames)
                if cols_not_found:
                    raise CsvColumnsNotFound(
                        "Columns {} are not found in {}.".format(
                            cols_not_found, filespec.filename
                        )
                    )
                self._fieldnames = [new_col_name(col) for col in filespec.columns]
                fieldnames_map = {
                    new_col_name(col): old_col_name(col) for col in filespec.columns
                }
            self._rows = (
                {c: row[fieldnames_map[c]] for c in self._fieldnames} for row in reader
            )
            self._valid = True
        else:
            if _fieldnames is None or _rows is None:
                raise TypeError("{} need filespec".format(self.__class__.__name__))
            # for internal use only
            self._rows = _rows
            self._fieldnames = _fieldnames
            self._valid = True

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """tuple: Get all field names including original and new columns"""
        return tuple(self._fieldnames) + tuple(self._new_fieldnames)

    @property
    def rows(self) -> Iterator[dict[str, str]]:
        """iterator: Get all rows with transformations applied"""
        return self._get_rows()

    @property
    def rows_typed(self) -> Iterator[dict[str, Any]]:
        """iterator: Get all rows with type conversions applied"""
        return self._get_rows(typed=True)

    def _get_rows(self, typed: bool = False) -> Iterator[dict[str, Any]]:
        if not self._valid:
            raise NotValidContent
        self._valid = False
        computed_cols = set(colname for colname, _ in self._applied)
        for row in self._rows:
            if self._applied or self._filters or typed:
                typed_row = row.copy()
                typed_row.update(
                    {
                        c: t(row[c])
                        for c, t in self._types.items()
                        if c not in computed_cols
                    }
                )
            for colname, func in self._applied:
                row[colname] = func(typed_row)
                if colname in self._types:
                    typed_row[colname] = self._types[colname](row[colname])
                else:
                    typed_row[colname] = row[colname]
            filter_ok = True
            for func in self._filters:
                if not func(typed_row):
                    filter_ok = False
            if filter_ok:
                if typed:
                    yield typed_row
                else:
                    yield row

    def add_apply(self, colname: str, func: Callable[[dict[str, Any]], Any]) -> None:
        """Add a transformation to apply to a column.
        
        Args:
            colname (str): Name of the column (existing or new)
            func (callable): Function to transform the column value
        """
        if colname not in self._fieldnames:
            self._new_fieldnames.append(colname)
        self._applied.append((colname, func))

    def add_filter(self, func: Callable[[dict[str, Any]], bool]) -> None:
        """Add a filter function for rows.
        
        Args:
            func (callable): Function that returns True for rows to keep
        """
        self._filters.append(func)

    def add_type(self, colname: str, typ: Callable[[str], Any]) -> None:
        """Add a type conversion for a column.
        
        Args:
            colname (str): Name of the column
            typ: Type to convert to
        """
        self._types[colname] = typ

    def join(
        self,
        oth: 'ContentCsv',
        *,
        left: bool = False,
        right: bool = False,
        empty: bool = False
    ) -> 'ContentCsv':
        """Join with another CSV content.
        
        Args:
            oth (ContentCsv): Other CSV content to join with
            left (bool): Perform left outer join
            right (bool): Perform right outer join
            empty (bool): Include rows with empty join keys
            
        Returns:
            ContentCsv: New content with joined data
        """
        common = set(self.fieldnames).intersection(set(oth.fieldnames))
        dict_of_oth = {}
        for l in oth.rows:
            value = tuple(l[k] for k in common)
            if not empty and all(not bool(x) for x in value):
                continue
            if value not in dict_of_oth:
                dict_of_oth[value] = []
            dict_of_oth[value].append(l)
        left_added_keys = [k for k in self.fieldnames if k not in common]
        added_keys = [k for k in oth.fieldnames if k not in common]
        new_fieldnames = list(self.fieldnames) + added_keys
        return ContentCsv(
            _fieldnames=new_fieldnames,
            _rows=_join_rowgen(
                self.rows, dict_of_oth, common, left_added_keys, added_keys, left, right
            ),
        )

    def concat(self, oth: 'ContentCsv') -> 'ContentCsv':
        """Concatenate with another CSV content.
        
        Args:
            oth (ContentCsv): Other CSV content to concatenate
            
        Returns:
            ContentCsv: New content with concatenated data
        """
        only_self = set(self.fieldnames).difference(set(oth.fieldnames))
        only_oth = set(oth.fieldnames).difference(set(self.fieldnames))
        new_fieldnames = list(self.fieldnames) + [
            k for k in oth.fieldnames if k in only_oth
        ]
        return ContentCsv(
            _fieldnames=new_fieldnames,
            _rows=_cat_rowgen(self.rows, oth.rows, only_self, only_oth),
        )

    def aggregate(
        self,
        keys: list[str] | None,
        aggregations: list[tuple[str, Callable[[dict[str, list[Any]]], Any]]] | None
    ) -> 'ContentCsv':
        """Aggregate rows by keys.
        
        Args:
            keys (list): Columns to group by
            aggregations (list): List of (column, function) pairs for aggregation
            
        Returns:
            ContentCsv: New content with aggregated data
        """
        if aggregations is None:
            aggregations = ()
        if keys is None:
            keys = ()

        stored_by_key_data_column = {}
        for row in self._get_rows(typed=True):
            keyvalue = tuple(row[k] for k in keys)
            if keyvalue not in stored_by_key_data_column:
                store = {colname: [] for colname in self.fieldnames}
                stored_by_key_data_column[keyvalue] = store
            else:
                store = stored_by_key_data_column[keyvalue]
            for colname, value in row.items():
                store[colname].append(value)
        new_fieldnames = [
            colname
            for colname in self.fieldnames
            if all(
                len(set(store[colname])) == 1
                for store in stored_by_key_data_column.values()
            )
        ]
        new_fieldnames.extend(
            colname for colname, _ in aggregations if colname not in new_fieldnames
        )
        return ContentCsv(
            _fieldnames=new_fieldnames,
            _rows=_aggregate_row_gen(
                new_fieldnames, stored_by_key_data_column, aggregations
            ),
        )

    def sort(
        self,
        keys: tuple[str, ...] = tuple(),
        numeric: bool = False,
        reverse: bool = False,
        random_sort: bool = False
    ) -> 'ContentCsv':
        """Sort the content.
        
        Args:
            keys (list): Columns to sort by
            numeric (bool): Try to sort numerically
            reverse (bool): Sort in reverse order
            random_sort (bool): Add random tie-breaker
            
        Returns:
            ContentCsv: New content with sorted data
        """
        if keys is None:
            keys = ()
        if numeric:
            cast_numeric = _cast_pseudo_numerical
        else:
            cast_numeric = lambda x: x

        if random_sort:
            append_random = lambda t: t + (random.random(),)
        else:
            append_random = lambda t: t

        key_fun = lambda row: append_random(tuple(cast_numeric(row[k]) for k in keys))

        return ContentCsv(
            _fieldnames=self.fieldnames,
            _rows=(row for row in sorted(self.rows, key=key_fun, reverse=reverse)),
        )

    def write(
        self,
        f: Any,
        *,
        delim: str = ",",
        fmt: list[ColFormat] | None = None
    ) -> None:
        """Write content to a CSV file.
        
        Args:
            f: File-like object to write to
            delim (str): CSV delimiter character
            fmt (list): List of ColFormat objects to apply
        """
        dialect = csv.excel
        dialect.delimiter = delim
        writer = csv.DictWriter(f, self.fieldnames, dialect=dialect)
        writer.writeheader()
        for l in self.rows:
            row = l.copy()
            for colfmt in fmt:
                colfmt.format(row)
            writer.writerow(row)
