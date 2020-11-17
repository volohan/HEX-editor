from PyQt5 import QtWidgets
from bytes_buffer import Buffer


# Открытие файла
def open_file():
    file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
    return Buffer(file_name)


# Сохраниение файла
def save_file(buffer):
    file_name = QtWidgets.QFileDialog.getSaveFileName()[0]
    with open(file_name, 'wb') as file:
        buffer.write_data(file)
