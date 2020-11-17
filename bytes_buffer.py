import hex_logging
import os


class Buffer:
    def __init__(self, file_name):
        self.row_count = 30
        self.encoding = 'mac_cyrillic'
        self._16_base = ['0', '1', '2', '3', '4', '5', '6', '7',
                         '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        # Запоминание данных
        self.file = open(file_name, 'br')
        self.file_size = os.path.getsize(file_name)
        self.extended_bytes = {}
        self.logger = hex_logging.Logger(self.extended_bytes)
        self.update_data(0)

    def get_size(self):
        res = self.file_size
        for bytes in self.extended_bytes.values():
            res += len(bytes) - 1
        return res

    def write_data(self, file):
        self.file.seek(0)
        for i in sorted(self.extended_bytes.keys()):
            while i - file.tell() > 4194304:
                file.write(self.file.read(4194304))
            file.write(self.file.read(i - file.tell()))
            file.write(self.extended_bytes[i])
        data = self.file.read(4194304)
        while len(data) != 0:
            file.write(data)
            data = self.file.read(4194304)

    # Обновление сдвига
    def update_data(self, shift):
        self.tens_offset = shift

        start = shift * 16
        iter = 0
        self.shown = bytearray()
        self.byte_index = {}

        for i in sorted(self.extended_bytes.keys()):
            if i < start:
                if i + len(self.extended_bytes[i]) < start:
                    if len(self.extended_bytes[i]) == 0:
                        start += 1
                    elif len(self.extended_bytes[i]) > 1:
                        start -= len(self.extended_bytes[i]) - 1
                    self.byte_index[-1] = start - 1
                else:
                    shift = start - i
                    start = i + 1
                    for _ in self.extended_bytes[i][:shift]:
                        iter -= 1
                        self.byte_index[iter] = i
                    iter = 0
                    for byte in self.extended_bytes[i][shift:]:
                        self.byte_index[iter] = i
                        iter += 1
                        self.shown.append(byte)
                    break
            else:
                break

        self.file.seek(start)
        if self.file.tell() != 0:
            self.byte_index[-1] = self.file.tell() - 1

        while len(self.shown) < self.row_count * 16:
            pos = self.file.tell()
            byte = self.file.read(1)
            if byte == b'':
                break
            if pos in self.extended_bytes:
                for byte in self.extended_bytes[pos]:
                    self.byte_index[iter] = pos
                    iter += 1
                    self.shown.append(byte)
            else:
                self.byte_index[iter] = pos
                iter += 1
                self.shown.append(byte[0])

    # Обновление данных относительно позиции из hex поля
    def update_from_hex_position(self, position, char, is_insert):
        if char in self._16_base:
            index = position // 3
            if position % 3 == 0:
                if position != len(self.shown) * 3 and is_insert:
                    new = char
                    new += self.shown[index:index + 1].hex()[1:]
                    self.add_byte(index, bytes.fromhex(new), True)
                else:
                    self.add_byte(index, bytes.fromhex(f'{char}0'), False)
                position += 1
            else:
                new = self.shown[index:index + 1].hex()[:1]
                new += char
                self.add_byte(index, bytes.fromhex(new), True)
                position += 2
        return position

    def add_byte(self, index, byte, is_insert):
        if not is_insert:
            index -= 1
        try:
            if self.byte_index[index] in self.extended_bytes:
                shift = 0
                try:
                    while self.byte_index[index - shift - 1] == self.byte_index[index]:
                        shift += 1
                except KeyError:
                    pass
                log = hex_logging.LogRecord(self.byte_index[index], self.extended_bytes[self.byte_index[index]], byte, shift, is_insert)
                if is_insert:
                    self.extended_bytes[self.byte_index[index]][shift] = byte[0]
                else:
                    self.extended_bytes[self.byte_index[index]].insert(shift + 1,
                                                                       byte[0])
            else:
                new = bytearray()
                if is_insert:
                    log = hex_logging.LogRecord(self.byte_index[index], None,
                                                          byte, 0,
                                                          is_insert)
                elif index != -1:
                    new = bytearray(self.shown[index: index + 1])
                    log = hex_logging.LogRecord(self.byte_index[index], None,
                                                          byte, 1,
                                                          is_insert)
                else:
                    self.file.seek(self.byte_index[index])
                    new = bytearray(self.file.read(1))
                    log = hex_logging.LogRecord(self.byte_index[index], None,
                                                          byte, 1,
                                                          is_insert)
                new.append(byte[0])
                self.extended_bytes[self.byte_index[index]] = new
        except KeyError:
            if 0 not in self.extended_bytes:
                self.extended_bytes[0] = self.shown[0:1]
            log = hex_logging.LogRecord(0, self.extended_bytes[0], byte, 1, is_insert)
            self.extended_bytes[0].insert(0, byte[0])
        self.logger.add(log)

    # Обновлении позиции относительно текстовых данных
    def update_from_text_position(self, position, char, is_insert):
        if char.isalnum():
            index = position - (position // 17)
            if position != len(self.shown) + (position // 17) and is_insert:
                self.add_byte(index, char.encode(self.encoding), True)
            else:
                self.add_byte(index, char.encode(self.encoding), False)
            if position % 17 == 15:
                position += 1
            if index == len(self.shown):
                position += 1
            position += 1
        return position

    def delete_byte(self, index):
        if self.byte_index[index] in self.extended_bytes:
            shift = 0
            try:
                while self.byte_index[index - 1 - shift] == self.byte_index[index]:
                    shift += 1
            except KeyError:
                pass
            log = hex_logging.LogRecord(self.byte_index[index], self.extended_bytes[self.byte_index[index]], b'', shift, True)
            self.extended_bytes[self.byte_index[index]].pop(shift)
        else:
            log = hex_logging.LogRecord(self.byte_index[index], None, b'', 0, True)
            self.extended_bytes[self.byte_index[index]] = bytearray()
        self.logger.add(log)

    # Стирание данных относительно hex позиции
    def backspace_event_from_text(self, position):
        index = position - (position // 17) - 1
        self.delete_byte(index)

        position -= 1
        if position % 17 == 16:
            position -= 1
        return position

    # Стирание данных относительно текстовой позиции
    def backspace_event_from_hex(self, position):
        if position % 3 == 0 and position != 0:
            index = position // 3 - 1
            self.delete_byte(index)
            position -= 3

        if position % 17 == 16:
            position -= 1
        return position

    # Показ десятков
    def tens_count(self):
        end = self.tens_offset + len(self.shown) // 16 + 1

        return ''.join([str(hex(x))[2:].zfill(7) + '0\n'
                        for x in range(self.tens_offset, end)])

    # Показ строки с единицами
    def units_count(self):
        return ' '.join([f'0{digit}' for digit in self._16_base])

    # Возврат данных в hex виде
    def to_hex(self):
        _hex = self.shown.hex()
        hex_list = [_hex[i:i + 2] for i in range(0, len(_hex), 2)]

        if len(hex_list) % 16 != 0:
            for i in range(0, 16 - len(hex_list) % 16):
                hex_list.append('')

        return '\n'.join([' '.join([hex_list[j] for j in range(i, i + 16)])
                          for i in range(0, len(hex_list), 16)]).rstrip() + ' '

    # Возврат данных в текстовом виде
    def to_text(self):
        text = ''.join([self.char_decrypt(i) for i in range(len(self.shown))])

        res = '\n'.join([text[i:i + 16] for i in range(
            0, len(text) - len(text) % 16, 16)])

        return (res + f'\n{text[len(text) - len(text) % 16:]}').lstrip('\n')

    # Перевод байтов в символы
    def char_decrypt(self, index):
        res = ''
        if self.shown[index] != '':
            if self.shown[index] < 20:
                res += '.'
            else:
                res += self.shown[index:index+1].decode(self.encoding)
        return res
