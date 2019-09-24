#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from cardinality import (
    format_cardinality,
    check_keys,
    examine_relation,
    main,
    parse_args,
    is_file,
)


def get_testfile_path(filename):
    """Return path to a test file."""
    test_file_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'test_files')
    return os.path.join(test_file_dir, filename)


class TestFormatCardinality():

    def test_format_cardinality(self):
        assert format_cardinality((0, 1), (2, 3)) == '0,1 to 2,3'


class TestCheckKeys():

    pk_frame = pd.DataFrame({
        'pk': [1, 2, 3, 4, 5],
        'pk_null': [1, 2, 3, 4, np.nan],
        'pk_duplicated': [1, 2, 3, 4, 4]})

    fk_frame_empty = pd.DataFrame({'fk': []})
    fk_frame_zero_one = pd.DataFrame({'fk': [1, 2, 2, 4, np.nan]})
    fk_frame_alien = pd.DataFrame({'fk': [1, 1, 3, 3, 6]})

    def test_check_keys_ok(self):
        check_keys(self.pk_frame[['pk']], self.fk_frame_zero_one)

    def test_check_keys_different_columns(self):
        with pytest.raises(AssertionError):
            check_keys(self.pk_frame, self.fk_frame_zero_one)

    def test_check_keys_pk_nan(self):
        with pytest.raises(AssertionError):
            check_keys(self.pk_frame[['pk_null']], self.fk_frame_zero_one)

    def test_check_keys_pk_duplicated(self):
        with pytest.raises(AssertionError):
            check_keys(
                self.pk_frame[['pk_duplicated']],
                self.fk_frame_zero_one)

    def test_check_keys_fk_empty(self):
        check_keys(self.pk_frame[['pk']], self.fk_frame_empty)

    def test_check_keys_fk_alien(self):
        with pytest.raises(AssertionError):
            check_keys(self.pk_frame[['pk']], self.fk_frame_alien)


class TestCardinality():

    pk_frame = pd.DataFrame({'pk': [1, 2, 3, 4, 5]})
    fk_frame_one_one = pd.DataFrame({'fk': [1, 2, 3, 4, 5]})
    fk_frame_zero_one = pd.DataFrame({'fk': [1, 2, 3, 4, np.nan]})
    fk_frame_two_three = pd.DataFrame({'fk': [1, 2, 2, 3, 4, 5]})
    fk_frame_empty = pd.DataFrame({'fk': []})

    def test_relation_one_one(self):
        assert examine_relation(
            self.pk_frame, self.fk_frame_one_one) == ((1, 1), (1, 1))

    def test_relation_zero_one(self):
        assert examine_relation(
            self.pk_frame, self.fk_frame_zero_one) == ((0, 1), (0, 1))

    def test_relation_two_three(self):
        assert examine_relation(
            self.pk_frame, self.fk_frame_two_three) == ((1, 1), (1, 2))

    def test_relation_empty(self):
        assert examine_relation(
            self.pk_frame, self.fk_frame_empty) == ((0, 0), (0, 0))


class TestArgumentParser():

    def test_parser_help(self):
        with pytest.raises(SystemExit):
            parse_args(['-h'])

    def test_parser(self):
        pk_file = get_testfile_path('pk-data.tsv')
        fk_file = get_testfile_path('fk-data.tsv')

        parser = parse_args([pk_file, fk_file, '-p', 'pk', '-f', 'fk'])
        assert parser.pk_file == pk_file
        assert parser.fk_file == fk_file
        assert parser.pk_columns == ['pk']
        assert parser.fk_columns == ['fk']

    def test_is_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            assert is_file(tmp.name) == tmp.name

    def test_is_file_error(self):
        with pytest.raises(argparse.ArgumentTypeError):
            is_file('')


class TestMain():

    pk_file = get_testfile_path('pk-data.tsv')
    fk_file = get_testfile_path('fk-data.tsv')

    def test_noargs(self):
        with pytest.raises(SystemExit):
            main()

    def test_args_help(self):
        with pytest.raises(SystemExit):
            main(['-h'])

    def test_args(self, capsys):
        main([self.pk_file, self.fk_file, '-p', 'pk', '-f', 'fk'])
        out, err = capsys.readouterr()
        assert out.rstrip() == '0,1 to 0,3'
        assert err == ''

    def test_args_verbose(self, capsys):
        main([self.pk_file, self.fk_file, '-v', '-p', 'pk', '-f', 'fk'])
        out, err = capsys.readouterr()
        assert out.rstrip() == (
            self.pk_file + '\t' + self.fk_file + '\tpk\tfk\t0,1 to 0,3')
        assert err == ''
