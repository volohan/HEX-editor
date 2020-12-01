import sys
from PyQt5 import QtWidgets, QtGui
from ui import UiMainWindow
from file_manager import open_file, save_file
from cursor_manager import cursor_controller_for_text, \
    cursor_controller_for_hex

__version__ = '2'
__author__ = 'Volokhan Nikolai'


# Действия для журналирования
def action_for_logger(func):
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

        try:
            self.bytes_buffer.searcher.start()
        except AttributeError:
            pass

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

        self.ui.multicursor_action.triggered.connect(self.add_cursor)
        self.ui.scroll_bar.valueChanged.connect(self.reset_cursors)
        self.ui.cursor_reset_action.triggered.connect(self.reset_cursors)

    # Показ файла
    def show_file(self):
        self.bytes_buffer.update_data(self.ui.scroll_bar.value())
        self.ui.bytes_field.setText(self.bytes_buffer.to_hex())
        self.ui.bytes_decryption_field.setText(self.bytes_buffer.to_text())
        self.ui.count_units.setText(self.bytes_buffer.units_count())
        self.ui.count_tens.setText(self.bytes_buffer.tens_count())
        size = self.bytes_buffer.get_size() // 16
        if self.bytes_buffer.get_size() % 16 == 0:
            size -= 1
        self.ui.scroll_bar.setRange(0, size)

    # Добавление курсора для мультикурсора
    def add_cursor(self):
        self.bytes_buffer.cursors.append(
            self.ui.bytes_field.textCursor().position())

    # Сброс курсоров
    def reset_cursors(self):
        self.bytes_buffer.cursors = []

    # Открытие файла
    def dialog_to_open(self):
        try:
            self.bytes_buffer = open_file()
            self.ui.undo_action.triggered.connect(self.undo)
            self.ui.redo_action.triggered.connect(self.redo)
            self.ui.search_action.triggered.connect(self.search)
            self.show_file()
            self.ui.scroll_bar.setValue(0)
            self.ui.bytes_field.setReadOnly(False)
            self.ui.bytes_decryption_field.setReadOnly(False)
        except FileNotFoundError:
            pass

    # Поисковик
    def search(self):
        self.bytes_buffer.search()
        self.bytes_buffer.searcher.change_count.connect(
            lambda count: self.set_suffix(self.bytes_buffer.searcher.count))
        self.ui.text_line.textChanged.connect(
            self.bytes_buffer.searcher.set_required)
        self.ui.down_button.clicked.connect(
            lambda: self.ui.count.setValue(self.bytes_buffer.searcher.next()))
        self.ui.up_button.clicked.connect(
            lambda: self.ui.count.setValue(self.bytes_buffer.searcher.prev()))
        self.bytes_buffer.searcher.reset_signal.connect(self.reset)
        self.ui.count.valueChanged.connect(
            lambda: self.bytes_buffer.searcher.set_current(
                self.ui.count.value()))
        self.bytes_buffer.searcher.go_signal.connect(self.go)

    # Оповещение о количестве совпадений
    def set_suffix(self, count):
        self.ui.count.setSuffix(f"/{count}")
        self.ui.count.setMaximum(count)

    # Сброс курсоров
    def reset(self):
        self.ui.count.setValue(0)
        self.set_suffix(0)

    # Переход на позицию
    def go(self, index, shift):
        pos = self.bytes_buffer.get_position(index, shift)
        row = pos // 16
        self.ui.scroll_bar.setValue(row)
        cursor = self.ui.bytes_field.textCursor()
        cursor.setPosition(pos % 16 * 3)
        cursor.movePosition(QtGui.QTextCursor.Right,
                            QtGui.QTextCursor.KeepAnchor,
                            len(self.bytes_buffer.searcher.required) * 3)
        self.ui.bytes_field.setTextCursor(cursor)

    @action_for_logger
    def undo(self):
        self.bytes_buffer.logger.undo()

    @action_for_logger
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
