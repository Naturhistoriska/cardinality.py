#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Examine the cardinality of a relation between two datasets."""

import argparse
import os
import sys

import pandas as pd


__author__ = 'Markus Englund'
__license__ = 'MIT'
__version__ = '0.1.0'


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = parse_args(args)

    pk_frame = pd.read_csv(
        parser.pk_file, usecols=parser.pk_columns, sep='\t')
    fk_frame = pd.read_csv(
        parser.fk_file, usecols=parser.fk_columns, sep='\t')

    check_keys(pk_frame, fk_frame)

    pk_columns_string = ','.join(parser.pk_columns)
    fk_columns_string = ','.join(parser.fk_columns)

    left, right = examine_relation(pk_frame, fk_frame)

    cardinality_string = format_cardinality(left, right)

    if parser.verbose is True:
        print('\t'.join([
            parser.pk_file, parser.fk_file,
            pk_columns_string, fk_columns_string,
            cardinality_string]))
    else:
        print(cardinality_string)


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog='cardinality.py', description=(
            'Command-line utility for examining the cardinality '
            'of the relation between two TSV-files.'))
    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='show verbose output')
    parser.add_argument(
        'pk_file', metavar='pk-file', action=StoreExpandedPath,
        type=is_file, help='TSV-file with primary keys')
    parser.add_argument(
        'fk_file', metavar='fk-file', action=StoreExpandedPath,
        type=is_file, help='TSV-file with foreign keys')
    parser.add_argument(
        '-p', dest='pk_columns', metavar='column', type=str, nargs='+',
        help='primary key columns')
    parser.add_argument(
        '-f', dest='fk_columns', metavar='column', type=str, nargs='+',
        help='foreign key columns')
    return parser.parse_args(args)


class StoreExpandedPath(argparse.Action):
    """Invoke shell-like path expansion for user- and relative paths."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            filepath = os.path.abspath(os.path.expanduser(str(values)))
            setattr(namespace, self.dest, filepath)


def is_file(filename):
    """Check if a path is a file."""
    if not os.path.isfile(filename):
        msg = '{0} is not a file'.format(filename)
        raise argparse.ArgumentTypeError(msg)
    else:
        return filename


def check_keys(pk_frame, fk_frame):
    """Check the sanity of primary and foreign keys."""

    assert len(pk_frame.columns) == len(fk_frame.columns), (
        'The number of columns must be the same for primary and foreign keys')

    assert pk_frame.notnull().any(axis=1).all(), 'Primary keys cannot be null.'

    assert not pk_frame.duplicated().any(), 'Primary keys must be unique.'

    # Check that each foreign is a primary key
    distinct_foreign_keys = (
        fk_frame.dropna(how='all').drop_duplicates())
    merged = distinct_foreign_keys.merge(
        pk_frame, how='left', left_on=list(distinct_foreign_keys.columns),
        right_on=list(pk_frame.columns), indicator=True)
    fk_is_pk = (merged._merge == 'both').all()
    assert fk_is_pk, 'Every foreign key must match a primary key.'


def examine_relation(pk_frame, fk_frame):
    """
    Examine the cardinality of the relation between key columns
    in two DataFrames.

    Parameters
    ----------
    pk_frame : pandas.DataFrame
        Frame with primary key columns. The number of columns should
        be the same as for the `fk_frame`.
    fk_frame : pandas.DataFrame
        Frame with foreign key columns. The number of columns should
        be the same as for the `fk_frame`.

    Returns
    -------
    a tuple of two 2-tuples with the minimum and maximum cardinality
    for the left and right sides of the relation. By convention,
    `pk_frame` is placed to the left and `fk_frame` to the right.
    """

    # Check if there are relations at all
    if fk_frame.isnull().all(axis=1).all():
        left = (0, 0)
        right = (0, 0)
    else:
        # Examine the left side of the relation
        if fk_frame.notnull().any(axis=1).all():
            left = (1, 1)
        else:
            left = (0, 1)

        # Examine the right side of the relation
        merged = pk_frame.merge(
            fk_frame, how='left', left_on=list(pk_frame.columns),
            right_on=list(fk_frame.columns), indicator=True)
        if (merged._merge == 'left_only').any():
            right_min = 0
        else:
            right_min = merged.loc[
                merged._merge == 'both', list(fk_frame.columns)
            ].groupby(by=list(fk_frame.columns)).size().min()
        right_max = (
            fk_frame.dropna(how='all')
            .groupby(by=list(fk_frame.columns))
            .size().max())
        right = (right_min, right_max)

    return left, right


def format_cardinality(left_cardinality, right_cardinality):
    """Return a string describing the cardinality of the relation."""
    cardinality_string = (
        ','.join([str(x) for x in left_cardinality]) + ' to ' +
        ','.join([str(x) for x in right_cardinality])
    )
    return cardinality_string


if __name__ == '__main__':  # pragma: no cover
    main()
