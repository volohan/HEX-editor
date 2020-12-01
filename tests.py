import time
import unittest

from bytes_buffer import Buffer


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.buffer = Buffer("for_tests")

    def test_shown(self):
        expected = bytearray(b'abcdefghgklmnopqrst\r\n1234567890\r\n\xd0\x93'
                             b'\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2 '
                             b'\xd0\xbd\xd0\xb0 \xd0\xb2\xd1\x81\xd1\x91? '
                             b'\xd0\xa2\xd0\xb0\xd0\xba '
                             b'\xd0\xb2\xd1\x8b\xd0\xbd\xd0\xb5\xd1\x81\xd0'
                             b'\xb8 \xd0\xb6\xd0\xb5 '
                             b'\xd0\xbc\xd1\x83\xd1\x81\xd0\xbe\xd1\x80!')
        self.assertEqual(self.buffer.shown, expected)

    def test_simple_hex_change(self):
        expected = bytearray(b'abcdefghgklmnopqrst\r\xaa1234567890\r\n\xd0\x93'
                             b'\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2 '
                             b'\xd0\xbd\xd0\xb0 \xd0\xb2\xd1\x81\xd1\x91? '
                             b'\xd0\xa2\xd0\xb0\xd0\xba '
                             b'\xd0\xb2\xd1\x8b\xd0\xbd\xd0\xb5\xd1\x81\xd0'
                             b'\xb8 \xd0\xb6\xd0\xb5 '
                             b'\xd0\xbc\xd1\x83\xd1\x81\xd0\xbe\xd1\x80!')
        self.buffer.update_from_hex_position(60, 'a', True)
        self.buffer.update_data(self.buffer.tens_offset)
        self.assertEqual(self.buffer.shown, expected)
        self.assertEqual(self.buffer.extended_bytes, {20: bytearray(b'\xaa')})

    def test_simple_text_change(self):
        expected = bytearray(b'abcdefghgklmnopqrsta\n1234567890\r\n\xd0\x93'
                             b'\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2 '
                             b'\xd0\xbd\xd0\xb0 \xd0\xb2\xd1\x81\xd1\x91? '
                             b'\xd0\xa2\xd0\xb0\xd0\xba '
                             b'\xd0\xb2\xd1\x8b\xd0\xbd\xd0\xb5\xd1\x81\xd0'
                             b'\xb8 \xd0\xb6\xd0\xb5 '
                             b'\xd0\xbc\xd1\x83\xd1\x81\xd0\xbe\xd1\x80!')
        self.buffer.update_from_text_position(20, 'a', True)
        self.buffer.update_data(self.buffer.tens_offset)
        self.assertEqual(self.buffer.shown, expected)
        self.assertEqual(self.buffer.extended_bytes, {19: bytearray(b'a')})

    def test_simple_hex_delete(self):
        expected = bytearray(b'abcdefghgklmnoqrst\r\n1234567890\r\n\xd0\x93'
                             b'\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2 '
                             b'\xd0\xbd\xd0\xb0 \xd0\xb2\xd1\x81\xd1\x91? '
                             b'\xd0\xa2\xd0\xb0\xd0\xba '
                             b'\xd0\xb2\xd1\x8b\xd0\xbd\xd0\xb5\xd1\x81\xd0'
                             b'\xb8 \xd0\xb6\xd0\xb5 '
                             b'\xd0\xbc\xd1\x83\xd1\x81\xd0\xbe\xd1\x80!')
        self.buffer.backspace_event_from_hex(45)
        self.buffer.update_data(self.buffer.tens_offset)
        self.assertEqual(self.buffer.shown, expected)
        self.assertEqual(self.buffer.extended_bytes, {14: bytearray(b'')})

    def test_simple_text_delete(self):
        expected = bytearray(b'abcdefghgklmnopqrst\r\n1234567890\r\n\xd0\x93'
                             b'\xd0\xbe\xd1\x82\xd0\xbe\xd0 \xd0\xbd\xd0\xb0 '
                             b'\xd0\xb2\xd1\x81\xd1\x91? '
                             b'\xd0\xa2\xd0\xb0\xd0\xba '
                             b'\xd0\xb2\xd1\x8b\xd0\xbd\xd0\xb5\xd1\x81\xd0'
                             b'\xb8 \xd0\xb6\xd0\xb5 '
                             b'\xd0\xbc\xd1\x83\xd1\x81\xd0\xbe\xd1\x80!')
        self.buffer.backspace_event_from_text(45)
        self.buffer.update_data(self.buffer.tens_offset)
        self.assertEqual(self.buffer.shown, expected)
        self.assertEqual(self.buffer.extended_bytes, {42: bytearray(b'')})

    def test_tens_count(self):
        expected = '00000030\n00000040\n00000050\n'
        self.buffer.update_data(3)
        self.assertEqual(self.buffer.tens_count(), expected)

    def test_units_count(self):
        expected = '00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f'
        self.assertEqual(self.buffer.units_count(), expected)

    def test_to_hex(self):
        expected = 'd0 b2 d1 8b d0 bd d0 b5 d1 81 d0 b8 20 d0 b6 d0\nb5 20 ' \
                   'd0 bc d1 83 d1 81 d0 be d1 80 21 '
        self.buffer.update_data(4)
        self.assertEqual(self.buffer.to_hex(), expected)

    def test_to_text(self):
        expected = '–≤—Л–љ–µ—Б–Є –ґ–\nµ –Љ—Г—Б–Њ—А!'
        self.buffer.update_data(4)
        self.assertEqual(self.buffer.to_text(), expected)

    def test_get_size(self):
        expected = 93
        self.buffer.update_from_hex_position(40, 'a', False)
        self.buffer.update_data(1)
        self.assertEqual(self.buffer.get_size(), expected)

    def test_undo(self):
        expected = {7: bytearray(b'`'), 14: bytearray(b'd')}
        self.buffer.update_from_hex_position(23, '0', False)
        self.buffer.update_from_text_position(14, 'd', True)
        self.buffer.update_from_hex_position(23, 'a', False)
        self.buffer.logger.undo()
        self.assertEqual(self.buffer.extended_bytes, expected)

    def test_redo(self):
        expected = {7: bytearray(b'j'),
                    14: bytearray(b'd'),
                    8: bytearray(b'j')}
        self.buffer.update_from_hex_position(23, '0', False)
        self.buffer.update_from_text_position(14, 'd', True)
        self.buffer.update_from_hex_position(23, 'a', False)
        self.buffer.logger.redo()
        self.assertEqual(self.buffer.extended_bytes, expected)


if __name__ == '__main__':
    unittest.main()
