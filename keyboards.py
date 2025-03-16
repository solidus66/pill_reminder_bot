from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def main_menu():
    keyboard = [
        ['Добавить лекарство'],
        ['Просмотреть лекарства'],
        ['Изменить лекарство'],
        ['Удалить лекарство']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_menu(additional_buttons=None):
    keyboard = [['Назад'], ['В главное меню']]
    if additional_buttons:
        keyboard.insert(0, [btn[0] for btn in additional_buttons])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def confirm_menu(med_name):
    keyboard = [[InlineKeyboardButton("Подтвердить прием", callback_data=f"confirm_{med_name}")]]
    return InlineKeyboardMarkup(keyboard)
