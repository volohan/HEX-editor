from PyQt5.Qt import QThread, QObject
from PyQt5.QtCore import pyqtSignal


class Searcher(QObject):
    go_signal = pyqtSignal(int, int)
    change_count = pyqtSignal(int)
    reset_signal = pyqtSignal()

    def __init__(self, file_name, extended_bytes):
        super().__init__()
        self.file = open(file_name, "rb")
        self.required = b""
        self.count = 0
        self.current = 0
        self.coincidences = []
        self.extended_bytes = extended_bytes

    def next(self):
        return self.set_current(self.current + 1)

    def prev(self):
        return self.set_current(self.current - 1)

    def reset(self):
        self.count = 0
        self.current = 0
        self.coincidences = []
        self.reset_signal.emit()

    def set_current(self, value):
        if 1 <= value <= self.count:
            self.current = value
        if self.current > 0:
            index, shift = self.coincidences[self.current - 1]
            self.go_signal.emit(index, shift)
        return self.current

    def update_count(self, index, shift):
        self.coincidences.append((index, shift))
        self.count += 1
        self.change_count.emit(self.count)

    def set_required(self, required):
        try:
            self.required = bytes.fromhex(required)
        except ValueError:
            self.required = b''
        self.start()

    def start(self):
        try:
            if len(self.required) == 0:
                raise ValueError

            try:
                self.thread.exit()
            except AttributeError:
                pass

            self.reset()

            self.thread = QThread()
            self.search = Search(self.required, self.file, self.extended_bytes)
            self.search.moveToThread(self.thread)
            self.search.another_one_found.connect(self.update_count)
            self.thread.started.connect(self.search.run)
            self.thread.start()
        except ValueError:
            self.reset()


class Search(QObject):
    another_one_found = pyqtSignal(int, int)

    def __init__(self, required, file, extended_bytes):
        super().__init__()
        self.required = required
        self.file = file
        self.file.seek(0)
        self.extended_bytes = extended_bytes

    def initial_filling(self):
        while len(self.temp) < len(self.required):
            if self.file.tell() in self.extended_bytes:
                for byte in self.extended_bytes[self.file.tell()]:
                    self.temp.append(byte)

                self.file.read(1)
            else:
                self.temp.append(self.file.read(1)[0])

        remainder = len(self.temp) - len(self.required)
        self.temp = self.temp[:len(self.required)]

        if self.temp == self.required:
            self.another_one_found.emit(0, 0)

        try:
            for byte in self.extended_bytes[self.file.tell() - 1][-remainder:]:
                self.try_add(byte)
        except KeyError:
            pass

    def run(self):
        self.temp = bytearray()
        self.start = 0
        self.shift = 0

        self.initial_filling()

        pos = self.file.tell()
        next_byte = self.file.read(1)

        while next_byte != b'':
            if pos in self.extended_bytes:
                for byte in self.extended_bytes[pos]:
                    self.try_add(byte)
            else:
                self.try_add(next_byte[0])
            pos = self.file.tell()
            next_byte = self.file.read(1)

    def try_add(self, byte):
        if self.start in self.extended_bytes:
            self.shift += 1
            if len(self.extended_bytes[self.start]) == self.shift:
                self.shift = 0
                self.start += 1
        else:
            self.start += 1

        self.temp.pop(0)
        self.temp.append(byte)

        if self.temp == self.required:
            self.another_one_found.emit(self.start, self.shift)
