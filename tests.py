import unittest
from bytes_buffer import Buffer


class FakeCursor:
    def __init__(self, pos):
        self.pos = pos

    def position(self):
        return self.pos

    def setPosition(self, position):
        self.pos = position


class FakeUi:
    def __init__(self, check):
        self.insert_button = FakeButton(check)


class FakeButton:
    def __init__(self, check):
        self.check = check

    def isChecked(self):
        return self.check


class HexEditorTestCase(unittest.TestCase):
    def setUp(self):
        self.bytes_buffer = Buffer(b'adfadfvafwfgafdgafghhlfdlfelanalkklkawp')
        self.bytes_buffer.update_offset(0)

    def test_hex_simple(self):
        position = self.bytes_buffer.update_from_hex_position(1, 'a', True)

        self.assertEqual(position, 3)
        self.assertEqual(self.bytes_buffer.data[0], 106)

    def test_hex_insert(self):
        position = self.bytes_buffer.update_from_hex_position(3, 'a', True)

        self.assertEqual(position, 4)
        self.assertEqual(self.bytes_buffer.data[1], 164)

    def test_hex_not_insert(self):
        position = self.bytes_buffer.update_from_hex_position(3, 'a', False)

        self.assertEqual(position, 4)
        self.assertEqual(self.bytes_buffer.data[1], 160)

    def test_text_simple(self):
        cursor = FakeCursor(1)
        position = self.bytes_buffer.update_from_text_position(1, 'a', True)

        self.assertEqual(position, 2)
        self.assertEqual(self.bytes_buffer.data[1], 97)

    def test_text_not_insert(self):
        position = self.bytes_buffer.update_from_text_position(4, 'a', False)

        self.assertEqual(position, 5)
        self.assertEqual(self.bytes_buffer.data[4], 97)

    def test_hex_backspace(self):
        position = self.bytes_buffer.backspace_event_from_hex(6)

        self.assertEqual(position, 3)
        self.assertEqual(self.bytes_buffer.data[1], 102)

    def test_hex_backspace_cant(self):
        position = self.bytes_buffer.backspace_event_from_hex(7)

        self.assertEqual(position, 7)
        self.assertEqual(self.bytes_buffer.data[2], 102)

    def test_text_backspace(self):
        position = self.bytes_buffer.backspace_event_from_text(7)

        self.assertEqual(position, 6)
        self.assertEqual(self.bytes_buffer.data[7], 102)


if __name__ == '__main__':
    unittest.main()
