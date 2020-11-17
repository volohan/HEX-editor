import sys
from PyQt5 import QtWidgets
from ui import UiMainWindow
from file_manager import open_file, save_file
from cursor_manager import cursor_controller_for_text, \
    cursor_controller_for_hex

__version__ = '2'
__author__ = 'Volokhan Nikolai'


def logger_do(func):
    def do(self):
        bytes_field_position = self.ui.bytes_field.textCursor().position()
        bytes_decryption_field_position = \
            self.ui.bytes_decryption_field.textCursor().position()
        func(self)
        self.show_file()
        bytes_field_cursor = self.ui.bytes_field.textCursor()
        bytes_field_cursor.setPosition(bytes_field_position)
        bytes_decryption_field_cursor = \
            self.ui.bytes_decryption_field.textCursor()
        bytes_decryption_field_cursor.setPosition(
            bytes_decryption_field_position)
        self.ui.bytes_field.setTextCursor(bytes_field_cursor)
        self.ui.bytes_decryption_field.setTextCursor(
            bytes_decryption_field_cursor)

    return do


class HexEditor:
    def __init__(self):
        self._16_base = ['0', '1', '2', '3', '4', '5', '6', '7',
                         '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

        # Создание окна и привязывание функций к сигналам
        self.ui = UiMainWindow()
        self.ui.bytes_field.cursorPositionChanged.connect(
            lambda: cursor_controller_for_hex(self.ui))
        self.ui.bytes_decryption_field.cursorPositionChanged.connect(
            lambda: cursor_controller_for_text(self.ui))
        self.ui.open_action.triggered.connect(self.dialog_to_open)
        self.ui.save_action.triggered.connect(self.dialog_to_save)
        self.ui.scroll_bar.valueChanged.connect(self.show_file)

        self.ui.hex_field_key_pres.connect(self.update_from_hex_position)
        self.ui.text_field_key_pres.connect(self.update_from_text_position)
        self.ui.hex_field_backspace.connect(self.backspace_event_from_hex)
        self.ui.text_field_backspace.connect(self.backspace_event_from_text)

    # Показ файла
    def show_file(self):
        self.bytes_buffer.update_data(self.ui.scroll_bar.value())
        self.ui.bytes_field.setText(self.bytes_buffer.to_hex())
        self.ui.bytes_decryption_field.setText(self.bytes_buffer.to_text())
        self.ui.count_units.setText(self.bytes_buffer.units_count())
        self.ui.count_tens.setText(self.bytes_buffer.tens_count())
        self.ui.scroll_bar.setRange(
            0, self.bytes_buffer.get_size() // 16 - 1)

    # Открытие файла
    def dialog_to_open(self):
        try:
            self.bytes_buffer = open_file()
            self.ui.undo_action.triggered.connect(self.undo)
            self.ui.redo_action.triggered.connect(self.redo)
            self.show_file()
            self.ui.scroll_bar.setValue(0)
            self.ui.bytes_field.setReadOnly(False)
            self.ui.bytes_decryption_field.setReadOnly(False)
        except FileNotFoundError:
            pass

    @logger_do
    def undo(self):
        self.bytes_buffer.logger.undo()

    @logger_do
    def redo(self):
        self.bytes_buffer.logger.redo()

    # Сохраниение файла
    def dialog_to_save(self):
        try:
            save_file(self.bytes_buffer)
            self.ui.bytes_field.clear()
            self.ui.bytes_field.setReadOnly(True)
            self.ui.bytes_decryption_field.clear()
            self.ui.bytes_decryption_field.setReadOnly(True)
            self.ui.count_tens.clear()
            self.ui.count_units.clear()
            delattr(self, 'bytes_buffer')
        except FileNotFoundError:
            pass

    # Обновление данных относительно позиции из hex поля
    def update_from_hex_position(self, cursor, char):
        try:
            is_insert = self.ui.insert_button.isChecked()
            position = \
                self.bytes_buffer.update_from_hex_position(cursor.position(),
                                                           char,
                                                           is_insert)
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass

    # Обновлении позиции относительно текстовых данных
    def update_from_text_position(self, cursor, char):
        try:
            is_insert = self.ui.insert_button.isChecked()
            position = \
                self.bytes_buffer.update_from_text_position(cursor.position(),
                                                            char,
                                                            is_insert)
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass

    # Стирание данных относительно hex позиции
    def backspace_event_from_text(self, cursor):
        try:
            position = self.bytes_buffer.backspace_event_from_text(
                cursor.position())
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass

    # Стирание данных относительно текстовой позиции
    def backspace_event_from_hex(self, cursor):
        try:
            position = self.bytes_buffer.backspace_event_from_hex(
                cursor.position())
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    hex_editor = HexEditor()
    sys.exit(app.exec_())
