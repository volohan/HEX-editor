# Контролирует курсор, чтобы он себя правильно вёл в поле с переведом
def cursor_controller_for_text(ui):
    cursor = ui.bytes_decryption_field.textCursor()
    if cursor.position() % 17 == 16:
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, 1)
        ui.bytes_decryption_field.setTextCursor(cursor)


# Контролирует курсор, чтобы он себя правильно вёл в поле с hex данными
def cursor_controller_for_hex(ui):
    cursor = ui.bytes_field.textCursor()
    position = cursor.position()
    text = ui.bytes_field.toPlainText()
    if position != len(text) and text[position] == ' ':
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, 1)
        ui.bytes_field.setTextCursor(cursor)


# Корректировка курсора для перемещения через стрелки
def cursor_correcting_for_hex(cursor):
    if (cursor.position() - 1) % 3 == 0:
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
