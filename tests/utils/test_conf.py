# -*- coding: utf-8 -*-

import os
import socket
from unittest import TestCase

from tempfile import NamedTemporaryFile

from mock import patch, Mock

from oasislmf.utils.conf import load_ini_file, replace_in_file
from oasislmf.utils.exceptions import OasisException


class LoadInIFile(TestCase):
    def test_values_are_bool___values_are_correctly_converted_to_bool_value(self):
        f = NamedTemporaryFile(mode='w', delete=False)
        try:
            f.writelines([
                '[section]\n',
                'a = True\n',
                'b = False\n',
            ])
            f.close()

            conf = load_ini_file(f.name)

            self.assertTrue(conf['a'])
            self.assertFalse(conf['b'])
        finally:
            os.remove(f.name)

    def test_values_are_int___values_are_correctly_converted_to_int_value(self):
        f = NamedTemporaryFile(mode='w', delete=False)
        try:
            f.writelines([
                '[section]\n',
                'a = 1\n',
                'b = 2\n',
            ])
            f.close()

            conf = load_ini_file(f.name)

            self.assertEqual(1, conf['a'])
            self.assertEqual(2, conf['b'])
        finally:
            os.remove(f.name)

    def test_values_are_float___value_are_correctly_converted_to_int_value(self):
        f = NamedTemporaryFile(mode='w', delete=False)
        try:
            f.writelines([
                '[section]\n',
                'a = 1.1\n',
                'b = 2.2\n',
            ])
            f.close()

            conf = load_ini_file(f.name)

            self.assertEqual(1.1, conf['a'])
            self.assertEqual(2.2, conf['b'])
        finally:
            os.remove(f.name)

    def test_values_are_ip_addresses___values_are_converted_into_ip_string_format(self):
        f = NamedTemporaryFile(mode='w', delete=False)
        try:
            f.writelines([
                '[section]\n',
                'a = 127.0.0.1\n',
                'b = 127.127.127.127\n',
            ])
            f.close()

            conf = load_ini_file(f.name)

            ipf = lambda s: socket.inet_ntoa(socket.inet_aton(s))

            self.assertEqual(ipf('127.0.0.1'), conf['a'])
            self.assertEqual(ipf('127.127.127.127'), conf['b'])
        finally:
            os.remove(f.name)

    def test_values_are_string_values___values_are_unchanged(self):
        f = NamedTemporaryFile(mode='w', delete=False)
        try:
            f.writelines([
                '[section]\n',
                'a = first.value\n',
                'b = another value\n',
            ])
            f.close()

            conf = load_ini_file(f.name)

            self.assertEqual('first.value', conf['a'])
            self.assertEqual('another value', conf['b'])
        finally:
            os.remove(f.name)

    def test_io_error_is_raised_when_opening_file___exception_is_converted_to_oasis_exception(self):
        def raising_function(*args, **kwargs):
            raise IOError()

        with patch('io.open', Mock(side_effect=raising_function)), self.assertRaises(OasisException):
            load_ini_file('file_name')


class ReplaceInFile(TestCase):
    def test_more_var_names_are_given_than_values___error_is_raised(self):
        with self.assertRaises(OasisException):
            replace_in_file('first_path', 'second_path', ['fist_arg', 'second_arg'], ['first_val'])

    def test_more_var_values_are_given_than_values___error_is_raised(self):
        with self.assertRaises(OasisException):
            replace_in_file('first_path', 'second_path', ['fist_arg'], ['first_val', 'second_val'])

    def test_input_file_does_not_include_any_var_names___file_is_unchanged(self):
        input_file = NamedTemporaryFile(mode='w', delete=False)
        output_file = NamedTemporaryFile(mode='w', delete=False)
        try:
            # Close immediately so that replace_in_file can open it
            output_file.close()
            input_file.writelines([
                'some_var some_val\n',
            ])
            input_file.close()

            replace_in_file(input_file.name, output_file.name, ['first_arg', 'second_arg'], ['first_val', 'second_val'])

            with open(output_file.name) as f:
                data = f.read()

            self.assertEqual('some_var some_val\n', data)
        finally:
            os.remove(input_file.name)
            os.remove(output_file.name)

    def test_input_file_includes_some_var_names___input_names_are_replaced_with_values(self):
        input_file = NamedTemporaryFile(mode='w', delete=False)
        output_file = NamedTemporaryFile(mode='w', delete=False)
        try:
            # Close immediately so that replace_in_file can open it
            output_file.close()
            input_file.writelines([
                'some_var first_arg\n',
            ])
            input_file.close()

            replace_in_file(input_file.name, output_file.name, ['first_arg', 'second_arg'], ['first_val', 'second_val'])

            with open(output_file.name) as f:
                data = f.read()

            self.assertEqual('some_var first_val\n', data)
        finally:
            os.remove(input_file.name)
            os.remove(output_file.name)

    def test_io_error_is_raised_when_opening_file___exception_is_converted_to_oasis_exception(self):
        def raising_function(*args, **kwargs):
            raise IOError()

        with patch('io.open', Mock(side_effect=raising_function)), self.assertRaises(OasisException):
            replace_in_file('in', 'out', ['first_arg', 'second_arg'], ['first_val', 'second_val'])

    def test_os_error_is_raised_when_opening_file___exception_is_converted_to_oasis_exception(self):
        def raising_function(*args, **kwargs):
            raise OSError()

        with patch('io.open', Mock(side_effect=raising_function)), self.assertRaises(OasisException):
            replace_in_file('in', 'out', ['first_arg', 'second_arg'], ['first_val', 'second_val'])
