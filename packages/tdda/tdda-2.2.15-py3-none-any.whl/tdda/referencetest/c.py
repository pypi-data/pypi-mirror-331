"""
checkpandas.py: comparison mechanism for pandas dataframes (and CSV files)

Source repository: http://github.com/tdda/tdda

License: MIT

Copyright (c) Stochastic Solutions Limited 2016-2024
"""

import csv
import os
import sys

from collections import OrderedDict

from tdda.referencetest.basecomparison import (
    BaseComparison,
    Diffs,
    FailureDiffs,
)
from tdda.referencetest.pddates import infer_date_format
from tdda.pd.utils import is_string_col
from tdda.utils import nvl


import pandas as pd
import numpy as np


# TDDA_DIFF = 'tdda diff'
TDDA_DIFF = 'diff'


class PandasComparison(BaseComparison):
    """
    Comparison class for pandas dataframes (and CSV files).
    """

    tmp_file_counter = 0  # used to number otherwise-nameless temp files

    def get_temp_filename(self, ext=None):
        self.tmp_file_counter += 1
        ext = ext or '.parquet'
        return f'df{self.tmp_file_counter:03}{ext}'

    def __new__(cls, *args, **kwargs):
        return super(PandasComparison, cls).__new__(cls)

    def check_dataframe(
        self,
        df,
        ref_df,
        actual_path=None,
        expected_path=None,
        check_data=None,
        check_types=None,
        check_order=None,
        check_extra_cols=None,
        sortby=None,
        condition=None,
        precision=None,
        msgs=None,
        type_matching=None,
        create_temporaries=True,
    ):
        """
        Compare two pandas dataframes.

        Args:

            *df*
                            Actual dataframe
            *ref_df*
                            Expected dataframe
            *actual_path*
                            Path for file where actual dataframe originated,
                            used for error messages.
            *expected_path*
                            Path for file where expected dataframe originated,
                            used for error messages.
            *check_types*
                            Option to specify fields to use to compare types.
            *check_order*
                            Option to specify fields to use to compare field
                            order.
            *check_data*
                            Option to specify fields to use to compare cell
                            values.
            *check_extra_cols*
                            Option to specify fields in the actual dataset
                            to use to check that there are no unexpected
                            extra columns.
            *sortby*
                            Option to specify fields to sort by before
                            comparing.
            *condition*
                            Filter to be applied to datasets before comparing.
                            It can be ``None``, or can be a function that takes
                            a DataFrame as its single parameter and returns
                            a vector of booleans (to specify which rows should
                            be compared).
            *precision*
                            Number of decimal places to compare float values.
            *msgs*
                            Optional Diffs object.

            *type_matching* 'strict', 'medium', 'permissive'.
                            None is same as strict.

            *create_temporaries*  If True (the default), if the check fails,
                                  the actual result in the dataframe will be
                                  written to disk (usually as parquet).

        Returns:

            A FailureDiffs named tuple with:
              .failures     the number of failures
              .diffs        a Diffs object with information about
                            the failures

        All of the 'Option' parameters can be of any of the following:

            - ``None`` (to apply that kind of comparison to all fields)
            - ``False`` (to skip that kind of comparison completely)
            - a list of field names
            - a function taking a dataframe as its single parameter, and
              returning a list of field names to use.
        """
        diffs = msgs  # better name

        self.expected_path = expected_path
        self.actual_path = actual_path

        type_matching = type_matching or 'strict'
        diffs = nvl(diffs, Diffs())
        precision = nvl(precision, 6)

        check_types = resolve_option_flag(check_types, ref_df)
        check_extra_cols = resolve_option_flag(check_extra_cols, df)

        missing_cols = []
        extra_cols = []
        wrong_types = []
        wrong_ordering = False
        for c in check_types:
            if c not in list(df):
                missing_cols.append(c)
            elif not (
                types_match(df[c].dtype, ref_df[c].dtype, type_matching)
            ):
                wrong_types.append((c, df[c].dtype, ref_df[c].dtype))
        if check_extra_cols:
            extra_cols = set(check_extra_cols) - set(list(ref_df))
        if check_order != False and not missing_cols:
            check_order = resolve_option_flag(check_order, ref_df)
            order1 = [c for c in list(df) if c in check_order if c in ref_df]
            order2 = [c for c in list(ref_df) if c in check_order if c in df]
            wrong_ordering = order1 != order2

        same = not any(
            (missing_cols, extra_cols, wrong_types, wrong_ordering)
        )
        if not same:  # Just column structure, at this point
            self.different_column_structure(diffs)
            self.missing_columns_detected(diffs, missing_cols, ref_df)
            self.extra_columns_found(diffs, extra_cols, df)
            if wrong_types:
                for c, dtype, ref_dtype in wrong_types:
                    self.field_types_differ(diffs, c, dtype, ref_dtype)
            if wrong_ordering:
                self.different_column_orders(diffs, df, ref_df)

        if sortby:
            sortby = resolve_option_flag(sortby, ref_df)
            if any([c in sortby for c in missing_cols]):
                self.info('Cannot sort on missing columns')
            else:
                df.sort_values(sortby, inplace=True)
                ref_df.sort_values(sortby, inplace=True)

        if condition:
            df = df[condition(df)].reindex()
            ref_df = ref_df[condition(ref_df)].reindex()

        na, nr = len(df), len(ref_df)
        same_len = na == nr
        if not same_len:
            self.different_numbers_of_rows(diffs, na, nr)
            same = False

        if same:
            check_data = resolve_option_flag(check_data, ref_df)
            if check_data:
                check_data = [c for c in check_data if c not in missing_cols]
                df = df[check_data]
                ref_df = ref_df[check_data]
                if precision is not None:
                    rounded = df.round(precision).reset_index(drop=True)
                    ref_rounded = ref_df.round(precision).reset_index(
                        drop=True
                    )
                else:
                    rounded = df
                    ref_rounded = ref_df

                same_content = rounded.equals(ref_rounded)  # the check!

                if not same_content:
                    failures = []
                    for c in list(ref_rounded):
                        if not rounded[c].equals(ref_rounded[c]):
                            pdiffs = self.differences(
                                c, rounded[c], ref_rounded[c], precision
                            )
                            if pdiffs:
                                failures.append('Column values differ: %s' % c)
                                failures.append(pdiffs)
                    if failures:
                        self.failure(diffs, 'Contents check failed.')
                        for f in failures:
                            self.info(diffs, f)
                        same = False

        if not same and create_temporaries:
            self.write_temporaries(df, ref_df, diffs)
        return FailureDiffs(failures=0 if same else 1, diffs=diffs)

    def write_temporaries(self, actual, expected, msgs):
        differ = None
        actual_path = self.actual_path
        expected_path = self.expected_path
        if actual_path and expected_path:
            commonname = os.path.split(actual_path)[1]
            differ = self.compare_with(actual_path, expected_path)

        else:
            if actual_path:
                commonname = os.path.split(actual_path)[1]
            elif expected_path:
                commonname = os.path.split(expected_path)[1]
            else:
                commonname = self.get_temp_filename()
            if expected is not None and not expected_path:
                # no expected file, so write it
                tmpExpectedPath = os.path.join(
                    self.tmp_dir, 'expected-' + commonname
                )
                expected_path = tmpExpectedPath
                self._write_reference_dataframe(expected, tmpExpectedPath)
                if actual_path:
                    differ = self.compare_with(
                        actual_path, tmpExpectedPath, custom_diff_cmd=TDDA_DIFF
                    )
            if actual is not None and not actual_path:
                # no actual file, so write it
                tmpActualPath = os.path.join(
                    self.tmp_dir, 'actual-' + commonname
                )
                self._write_reference_dataframe(actual, tmpActualPath)
                if expected_path:
                    differ = self.compare_with(
                        tmpActualPath, expected_path, custom_diff_cmd=TDDA_DIFF
                    )

        if differ:
            self.info(msgs, differ)

        # if not actual_path or not expected_path:
        #     if expected_path:
        #         self.info(msgs, 'Expected file %s' % expected_path)
        #     elif actual_path:
        #         self.info(msgs,
        #                   'Actual file %s' % os.path.normpath(actual_path))

    def differences(self, name, values, ref_values, precision):
        """
        Args:
            name          is the name of the columns
            values        is the left-hand series
            ref_values    is the rish-hand series
            precision

        Returns a short summary of where values differ, for two columns.
        """
        print(values, type(values))
        print(ref_values, type(ref_values))
#        for i, val in enumerate(values):
#            refval = ref_values[i]
        valnull = values.isnull()
        refnull = ref_values.isnull()
        bothnull = valnull & refnull
        n_both_null = bothnull.sum()
        neither_null = np.logical_not(bothnull)
        assert bothnull.sum() < len(values)  # Shouldn't have got here
        if n_both_null == 0:
            (L, R) = (values, ref_values)
        else:
            (L, R) = (values[neither_null], ref_values[neither_null])
        same = L.eq(R)
        L = L[np.logical_not(same)][:10]
        R = R[np.logical_not(same)][:10]
        print(L)
        print(R)
#            summary_vals = sample_format2(L, precision)
#            summary_ref_vals = sample_format2(R, precision)
        summary_diffs = col_comparison(L, R, name)
        n = len(L)
        if n == 0:
            return ''
        s = (
            'First 10 differences'
            if n > 10
            else ('Difference%s' % ('s' if n > 1 else ''))
        )
 #           return '%s:\n[%s] != [%s]' % (s, summary_vals, summary_ref_vals)
        return col_comparison(L, R, name)

    def sample(self, values, start, stop):
        return [
            None if pd.isnull(values[i]) else values[i]
            for i in range(start, stop)
        ]

    def sample_format(self, values, start, stop, precision):
        s = self.sample(values, start, stop)
        r = ', '.join(
            [
                'null'
                if pd.isnull(v)
                else str('%d' % v)
                if type(v) in (int, np.int32, np.int64)
                else str('%.*f' % (precision, v))
                if type(v) in (float, np.float32, np.float64)
                else str('"%s"' % v)
                if values.dtype == object
                else str(v)
                for v in s
            ]
        )
        if len(s) < stop - start:
            r += ' ...'
        return r

    def ndifferences(self, values1, values2, start, limit=10):
        stop = min(start + limit, len(values1))
        for i in range(start, stop):
            v1 = values1[i]
            v2 = values2[i]
            if v1 == v2 or (pd.isnull(v1) and pd.isnull(v2)):
                return i
        return stop

    def check_serialized_dataframe(
        self,
        actual_path,
        expected_path,
        loader=None,
        check_data=None,
        check_types=None,
        check_order=None,
        condition=None,
        sortby=None,
        precision=6,
        msgs=None,
        **kwargs,
    ):
        """
        Checks two data frames on disk files are the same,
        by comparing them as dataframes.

        Args:

            *actual_path*
                            Pathname for actual CSV file.
            *expected_path*
                            Pathname for expected CSV file.
            *loader*
                            A function to use to read a CSV file to obtain
                            a pandas dataframe. If None, then a default CSV
                            loader is used, which takes the same parameters
                            as the standard pandas pd.read_csv() function.

            *check_data*
                            Option to specify fields to use to compare cell
                            values.
            *check_types*
                            Option to specify fields to use to compare types.

            *check_order*
                            Option to specify fields to use to compare field
                            order.

            *condition*
                            Filter to be applied to datasets before comparing.
                            It can be ``None``, or can be a function that takes
                            a DataFrame as its single parameter and returns
                            a vector of booleans (to specify which rows should
                            be compared).
            *sortby*
                            Option to specify fields to sort by before
                            comparing.
            *precision*
                            Number of decimal places to compare float values.
            *msgs*
                            Optional Diffs object.

            *\*\*kwargs*
                            Any additional named parameters are passed straight
                            through to the loader function.

        The other parameters are the same as those used by
        :py:mod:`check_dataframe`.
        Returns a tuple (failures, msgs), containing the number of failures,
        and a Diffs object containing error messages.
        """
        ref_df = self.load_serialized_dataframe(
            expected_path, loader=loader, **kwargs
        )
        df = self.load_serialized_dataframe(
            actual_path, loader=loader, **kwargs
        )
        return self.check_dataframe(
            df,
            ref_df,
            actual_path=actual_path,
            expected_path=expected_path,
            check_data=check_data,
            check_types=check_types,
            check_order=check_order,
            condition=condition,
            sortby=sortby,
            precision=precision,
            msgs=msgs,
        )

    check_csv_file = check_serialized_dataframe

    def check_serialized_dataframes(
        self,
        actual_paths,
        expected_paths,
        check_data=None,
        check_types=None,
        check_order=None,
        condition=None,
        sortby=None,
        msgs=None,
        **kwargs,
    ):
        """
        Wrapper around the check_serialized_dataframes() method,
        used to compare collections of serialized data frames on disk
        against reference counterparts

            *actual_paths*
                            List of pathnames for actual serialized data frames
            *expected_paths*
                            List of pathnames for expected serialized
                            data frames.
            *loader*
                            A function to use to read a CSV file to obtain
                            a pandas dataframe. If None, then a default CSV
                            loader is used, which takes the same parameters
                            as the standard pandas pd.read_csv() function.
            *\*\*kwargs*
                            Any additional named parameters are passed straight
                            through to the loader function.

            *check_data*
                            Option to specify fields to use to compare cell
                            values.
            *check_types*
                            Option to specify fields to use to compare types.

            *check_order*
                            Option to specify fields to use to compare field
                            order.

            *condition*
                            Filter to be applied to datasets before comparing.
                            It can be ``None``, or can be a function that takes
                            a DataFrame as its single parameter and returns
                            a vector of booleans (to specify which rows should
                            be compared).
            *sortby*
                            Option to specify fields to sort by before
                            comparing.
            *precision*
                            Number of decimal places to compare float values.
            *msgs*
                            Optional Diffs object.

        The other parameters are the same as those used by
        :py:mod:`check_dataframe`.
        Returns a tuple (failures, msgs), containing the number of failures,
        and a list of error messages.

        Returns a tuple (failures, msgs), containing the number of failures,
        and a Diffs object containing error messages.

        Note that this function compares ALL of the pairs of actual/expected
        files, and if there are any differences, then the number of failures
        returned reflects the total number of differences found across all
        of the files, and the msgs returned contains the error messages
        accumulated across all of those comparisons. In other words, it
        doesn't stop as soon as it hits the first error, it continues through
        right to the end.
        """
        if msgs is None:
            msgs = Diffs()
        failures = 0
        for actual_path, expected_path in zip(actual_paths, expected_paths):
            try:
                r = self.check_serialized_dataframe(
                    actual_path,
                    expected_path,
                    check_data=check_data,
                    check_types=check_types,
                    check_order=check_order,
                    sortby=sortby,
                    condition=condition,
                    msgs=msgs,
                    **kwargs,
                )
                (n, msgs) = r
                failures += n
            except Exception as e:
                self.info(
                    msgs,
                    'Error comparing %s and %s (%s %s)'
                    % (
                        os.path.normpath(actual_path),
                        expected_path,
                        e.__class__.__name__,
                        str(e),
                    ),
                )
                failures += 1
        return (failures, msgs)

    check_csv_files = check_serialized_dataframes

    def failure(self, msgs, s):
        """
        Add a failure to the list of messages, and also display it immediately
        if verbose is set. Also provide information about the two files
        involved.
        """
        if self.actual_path and self.expected_path:
            self.info(
                msgs,
                self.compare_with(
                    os.path.normpath(self.actual_path), self.expected_path
                ),
            )
        elif self.expected_path:
            self.info(msgs, 'Expected file %s' % self.expected_path)
        elif self.actual_path:
            self.info(msgs, 'Actual file %s'
                          % os.path.normpath(self.actual_path))
        self.info(msgs, s)

    def all_fields_except(self, exclusions):
        """
        Helper function, for using with *check_data*, *check_types* and
        *check_order* parameters to assertion functions for Pandas DataFrames.

        It returns the names of all of the fields in the DataFrame being
        checked, apart from the ones given.

        *exclusions* is a list of field names.
        """
        return lambda df: list(set(list(df)) - set(exclusions))

    def load_csv(self, csvfile, loader=None, **kwargs):
        """
        Function for constructing a pandas dataframe from a CSV file.
        """
        if loader is None:
            loader = default_csv_loader
        return loader(csvfile, **kwargs)

    def load_serialized_dataframe(
        self, path, actual_df=None, loader=None, **kwargs
    ):
        """
        Function for constructing a pandas dataframe from a serialized
        dataframe in a file (parquet or CSV)
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == '.parquet':
            try:
                return pd.read_parquet(path)
            except FileNotFoundError:
                if actual_df is not None:
                    tmp_path = self.tmp_path_for(path)
                    self._write_reference_dataframe(actual_df, tmp_path)
                    print(f'\n*** Expected parquet file {path} not found.\n')
                    print(self.compare_with(tmp_path, path))
                raise
        else:
            return self.load_csv(path, loader, **kwargs)

    def write_csv(self, df, csvfile, writer=None, **kwargs):
        """
        Function for saving a Pandas DataFrame to a CSV file.
        Used when regenerating DataFrame reference results.
        """
        if writer is None:
            writer = default_csv_writer
        writer(df, csvfile, **kwargs)

    def _write_reference_dataframe(
        self, df, path, writer=None, verbose=False, **kwargs
    ):
        """
        Function for saving a Pandas DataFrame to a CSV file.
        Used when regenerating DataFrame reference results.
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == '.parquet':
            df.to_parquet(path)
        else:
            self.write_csv(path, writer, **kwargs)
        if verbose:
            print(f'*** Written {path}.')


class PandasNotImplemented(object):
    """
    Null implementation of PandasComparison, used when pandas not available.
    """

    def __getattr__(self, name):
        return lambda *args, **kwargs: self.method(name, *args, **kwargs)

    def method(self, name, *args, **kwargs):
        raise NotImplementedError('%s: Pandas not available.' % name)


def default_csv_loader(csvfile, **kwargs):
    """
    Default function for reading a csv file.

    Wrapper around the standard pandas pd.read_csv() function, but with
    slightly different defaults:

        - index_col             is ``None``
        - infer_datetime_format is ``True``
        - quotechar             is ``"``
        - quoting               is :py:const:`csv.QUOTE_MINIMAL`
        - escapechar            is ``\\`` (backslash)
        - na_values             are the empty string, ``"NaN"``, and ``"NULL"``
        - keep_default_na       is ``False``
    """
    options = {
        'index_col': None,
        'quotechar': '"',
        'quoting': csv.QUOTE_MINIMAL,
        'escapechar': '\\',
        'na_values': ['', 'NaN', 'NULL'],
        'keep_default_na': False,
    }
    options.update(kwargs)
    if 'infer_datetime_format' in options:  # don't let pandas do it.
        del options['infer_datetime_format']
    infer_datetimes = kwargs.get('infer_datetime_format', True)

    try:
        df = pd.read_csv(csvfile, **options)
    except pd.errors.ParserError:
        # Pandas CSV reader gets confused by stutter-quoted text that
        # also includes escapechars. So try again, with no escapechar.
        del options['escapechar']
        df = pd.read_csv(csvfile, **options)

    if infer_datetimes:  # We do it ourselves, now, instead of lettings
        # pandas do it.
        colnames = df.columns.tolist()
        for c in colnames:
            if is_string_col(df[c]):
                fmt = infer_date_format(df[c])
                if fmt:
                    try:
                        datecol = pd.to_datetime(df[c], format=fmt)
                        if datecol.dtype == np.dtype('datetime64[ns]'):
                            df[c] = datecol
                    except Exception as e:
                        pass
        ndf = pd.DataFrame()
        for c in colnames:
            ndf[c] = df[c]
        return ndf
    else:
        return df


def default_csv_writer(df, csvfile, **kwargs):
    """
    Default function for writing a csv file.

    Wrapper around the standard pandas pd.to_csv() function, but with
    slightly different defaults:

        - index                 is ``False``
        - encoding              is ``utf-8``
    """
    options = {
        'index': False,
        'encoding': 'utf-8',
    }
    options.update(kwargs)
    if sys.version_info[0] > 2 and len(df) > 0:
        bytes_cols = find_bytes_cols(df)
        if bytes_cols:
            df = bytes_to_unicode(df, bytes_cols)
    return df.to_csv(csvfile, **options)


def find_bytes_cols(df):
    bytes_cols = []
    for c in list(df):
        if is_string_col(df[c]):
            nonnulls = df[df[c].notnull()].reset_index()[c]
            if len(nonnulls) > 0 and type(nonnulls[0]) is bytes:
                bytes_cols.append(c)
    return bytes_cols


def bytes_to_unicode(df, bytes_cols):
    cols = OrderedDict()
    for c in list(df):
        if c in bytes_cols:
            cols[unicode_definite(c)] = df[c].str.decode('UTF-8')
        else:
            cols[unicode_definite(c)] = df[c]
    return pd.DataFrame(cols, index=df.index.copy())


def unicode_definite(s):
    return s if type(s) == str else s.decode('UTF-8')


def resolve_option_flag(flag, df):
    """
    Method to resolve an option flag, which may be any of:

       ``None`` or ``True``:
                use all columns in the dataframe
       ``False``:
                use no columns
       list of columns
                use these columns
       function returning a list of columns
    """
    if flag is None or flag is True:
        return list(df)
    elif flag is False:
        return []
    elif hasattr(flag, '__call__'):
        return flag(df)
    else:
        return flag


def sample_format2(values, precision=None):
    return ', '.join(
        '%d: %s' % (values.index[i], values.iloc[i])
        for i in range(min(len(values), 10))
    )


def col_comparison(left, right, col_name):
    n = min(len(left), 10)
    indexes = [str(left.index[i]) for i in range(n)]
    lefts = [repr(left.iloc[i]) for i in range(n)]
    rights = [repr(right.iloc[i]) for i in range(n)]
    df = pd.DataFrame({
        'row': indexes,
        'actual ' + col_name: lefts,
        'expected ' + col_name: rights,
    })


def loosen_type(t):
    name = ''.join(c for c in t if not c.isdigit()).lower()
    p = name.find('[')
    name = name[:p] if p > -1 else name
    return 'bool' if name == 'boolean' else name


def types_match(t1, t2, level=None):
    assert level is None or level in ('strict', 'medium', 'permissive')
    if level is None or level == 'strict' or t1.name == t2.name:
        return t1.name == t2.name

    t1loose = loosen_type(t1.name)
    t2loose = loosen_type(t2.name)
    object_types = ('string', 'boolean', 'datetime', 'bool')
    if (
        t1loose == t2loose
        or t1loose == 'object'
        and t2loose in object_types
        or t2loose == 'object'
        and t1loose in object_types
    ):
        return True

    numeric_types = ('bool', 'boolean', 'int', 'float')
    if (
        level == 'permissive'
        and t1loose in numeric_types
        and t2loose in numeric_types
    ):
        return True
    return False
