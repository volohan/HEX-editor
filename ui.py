from PyQt5 import QtCore, QtGui, QtWidgets
from cursor_manager import cursor_correcting_for_hex


class UiMainWindow(QtWidgets.QMainWindow):
    hex_field_key_pres = QtCore.pyqtSignal(QtGui.QTextCursor, str)
    text_field_key_pres = QtCore.pyqtSignal(QtGui.QTextCursor, str)
    hex_field_backspace = QtCore.pyqtSignal(QtGui.QTextCursor)
    text_field_backspace = QtCore.pyqtSignal(QtGui.QTextCursor)

    def __init__(self):
        super().__init__()
        self.resize(640, 480)
        font = QtGui.QFont("Courier New", 12)
        font_metrics = QtGui.QFontMetrics(font)
        char_width = font_metrics.horizontalAdvance('a')
        char_height = font_metrics.height()

        # Установка центрального виджета
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Создание спэйсера
        spacer = QtWidgets.QSpacerItem(40, 20,
                                       QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum)

        # Создание поля с байтами
        self.bytes_field = QtWidgets.QTextEdit(self.central_widget)
        self.bytes_field.setFont(font)
        self.bytes_field.setMinimumWidth(char_width * 16 * 3)
        self.bytes_field.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.bytes_field.setReadOnly(True)
        self.bytes_field.keyPressEvent = self.hex_key_event
        self.bytes_field.wheelEvent = lambda _: None

        # Создание поля с перечислением десятков
        self.count_tens = QtWidgets.QTextEdit(self.central_widget)
        self.count_tens.setFixedWidth(char_width * 9)
        self.count_tens.setFont(font)
        self.count_tens.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.count_tens.setDisabled(True)

        # Создание поля с расшифровкой байтов
        self.bytes_decryption_field = QtWidgets.QTextEdit(self.central_widget)
        self.bytes_decryption_field.setFixedWidth(char_width * 17)
        self.bytes_decryption_field.setFont(font)
        self.bytes_decryption_field.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.bytes_decryption_field.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.bytes_decryption_field.setReadOnly(True)
        self.bytes_decryption_field.keyPressEvent = self.text_key_event
        self.bytes_decryption_field.wheelEvent = lambda _: None

        # Создание поля с перечислением единиц
        self.count_units = QtWidgets.QTextBrowser(self.central_widget)
        self.count_units.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.count_units.setMaximumHeight(char_height + 10)
        self.count_units.setFont(font)
        self.count_units.setDisabled(True)

        # Создание надписи "Offset(h)"
        self.lable = QtWidgets.QLabel()
        self.lable.setText("Offset(h)")
        self.lable.setFont(QtGui.QFont("Courier", 8, QtGui.QFont.Bold))
        font.setBold(True)
        self.lable.setFont(font)

        # Переключатель 'insert'
        self.insert_button = QtWidgets.QRadioButton()
        self.insert_button.setText("Insert")
        self.insert_button.click()

        # Создаём scrollbar
        self.scroll_bar = QtWidgets.QScrollBar()
        self.scroll_bar.setRange(0, 0)

        # Создаём layout для интерфейса
        self.layout = QtWidgets.QGridLayout()
        self.layout.addItem(spacer, 1, 0, 1, 1)
        self.layout.addWidget(self.bytes_field, 1, 2, 1, 1)
        self.layout.addWidget(self.count_tens, 1, 1, 1, 1)
        self.layout.addWidget(self.bytes_decryption_field, 1, 3, 1, 1)
        self.layout.addWidget(self.count_units, 0, 2, 1, 1)
        self.layout.addWidget(self.lable, 0, 1, 1, 1)
        self.layout.addWidget(self.insert_button, 0, 3, 1, 1)
        self.layout.addItem(spacer, 1, 4, 1, 1)

        # Создаём глобальный layout
        self.upper_layout = QtWidgets.QHBoxLayout()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.scroll_bar)

        self.global_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.global_layout.addLayout(self.upper_layout)
        self.global_layout.addLayout(self.main_layout)

        # Создание менюбара
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 22))

        # Создание полей менюбара
        self.file_menu = QtWidgets.QMenu(self.menubar)
        self.search_action = QtWidgets.QAction(self.menubar)
        self.undo_action = QtWidgets.QAction(self.menubar)
        self.redo_action = QtWidgets.QAction(self.menubar)
        self.setMenuBar(self.menubar)

        # Создание подпунктов вкладки "Файл" в меню
        self.open_action = QtWidgets.QAction(self)
        self.save_action = QtWidgets.QAction(self)

        # Установка подпунктов
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.search_action)
        self.menubar.addAction(self.undo_action)
        self.menubar.addAction(self.redo_action)

        # Перевод интерфейса
        self.retranslate_ui()

        self.search_action.triggered.connect(self.add_search_field)

        self.multicursor_action = QtWidgets.QAction("Multicursor",
                                                    self.bytes_field)
        self.multicursor_action.setShortcut(
            QtGui.QKeySequence("Ctrl+Q"))
        self.bytes_field.addAction(self.multicursor_action)

        self.cursor_reset_action = QtWidgets.QAction("Multicursor",
                                                     self.bytes_field)
        self.cursor_reset_action.setShortcut(
            QtGui.QKeySequence("Ctrl+R"))
        self.bytes_field.addAction(self.cursor_reset_action)

        self.show()

    def fake(self, a):
        pass

    # Переименовывание элесентов
    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "HEX-editor"))
        self.file_menu.setTitle(_translate("self", "Файл"))
        self.search_action.setText(_translate("self", "Поиск"))
        self.open_action.setText(_translate("self", "Открыть"))
        self.save_action.setText(_translate("self", "Сохранить"))
        self.undo_action.setText(_translate("self", "undo"))
        self.redo_action.setText(_translate("self", "redo"))

    # Действие на нажатие клавиши на панели с hex данными
    def hex_key_event(self, event):
        cursor = self.bytes_field.textCursor()
        if event.key() == QtCore.Qt.Key_Left:
            # Стрелка влево
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 3)
        elif event.key() == QtCore.Qt.Key_Right:
            # Стрелка вправо
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, 3)
        elif event.key() == QtCore.Qt.Key_Up:
            # Стрелка вверх
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Up, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Down:
            # Стрелка вниз
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Down, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            # Действие на backspce
            self.hex_field_backspace.emit(cursor)
        else:
            # Ввод текста в поле с hex данными
            self.hex_field_key_pres.emit(cursor, event.text())
        self.bytes_field.setTextCursor(cursor)

    # Действие на нажатие клавиши на панели с переводом
    def text_key_event(self, event):
        cursor = self.bytes_decryption_field.textCursor()
        if event.key() == QtCore.Qt.Key_Left:
            # Стрелка влево
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
            if cursor.position() % 17 == 16:
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Right:
            # Стрелка вправо
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Up:
            # Стрелка вверх
            cursor.movePosition(cursor.Up, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Down:
            # Стрелка вниз
            cursor.movePosition(cursor.Down, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            # Действие на backspace
            self.text_field_backspace.emit(cursor)
        else:
            # Ввод текста в поле
            self.text_field_key_pres.emit(cursor, event.text())
        self.bytes_decryption_field.setTextCursor(cursor)

    def add_search_field(self):
        self.del_upper_field()

        self.text_line = QtWidgets.QLineEdit()

        self.count = QtWidgets.QSpinBox()
        self.count.setFixedWidth(100)
        self.count.setSuffix("/0")
        self.count.setMaximum(0)
        self.count.setButtonSymbol(QtWidgets.QAbstractSpinBox.NoButtons)

        self.down_button = QtWidgets.QPushButton()
        self.down_button.setFixedWidth(50)
        self.up_button = QtWidgets.QPushButton()
        self.up_button.setFixedWidth(50)
        self.close_button = QtWidgets.QPushButton()
        self.close_button.setFixedWidth(50)
        self.close_button.setFixedHeight(35)
        self.close_button.setFont(QtGui.QFont("Courier New", 25))
        self.close_button.clicked.connect(self.del_upper_field)

        self.upper_layout.addWidget(self.text_line)
        self.upper_layout.addWidget(self.up_button)
        self.upper_layout.addWidget(self.down_button)
        self.upper_layout.addWidget(self.count)
        self.upper_layout.addWidget(self.close_button)

        self.down_button.setText("↓")
        self.up_button.setText("↑")
        self.close_button.setText("×")

    def del_upper_field(self):
        for i in reversed(range(self.upper_layout.count())):
            self.upper_layout.itemAt(i).widget().setParent(None)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = UiMainWindow()
    sys.exit(app.exec_())
