import os
from datetime import datetime, time
import pytz
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler
)
from telegram.ext.filters import Regex, Text
from telegram import Update
from dotenv import load_dotenv
from keyboards import main_menu, back_menu, confirm_menu
from db import load_db, save_db, update_stock

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
USER_ID = int(os.getenv('USER_ID'))

(
    ADD_NAME, ADD_FREQUENCY, ADD_TIME, ADD_STOCK, ADD_WARNING,
    DELETE_MED, EDIT_MED, EDIT_FIELD, EDIT_STOCK, EDIT_TIME,
    EDIT_NAME_VALUE,
    EDIT_ADD_STOCK
) = range(12)

MOSCOW_TZ = pytz.timezone('Europe/Moscow')

user_data = {}


def restrict_access(update: Update, context):
    if update.effective_user.id != USER_ID:
        update.message.reply_text("Доступ запрещён. Вы не авторизованы для использования этого бота.")
        return False
    return True


def validate_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


async def handle_navigation(update: Update, context):
    text = update.message.text
    current_state = context.user_data.get('current_state')
    print(f"Handling navigation - Received text: '{text}', Current state: {current_state}")

    if text in ["В главное меню", "в главное меню"]:
        print("Navigating to main menu")
        await update.message.reply_text("Возвращаемся в главное меню.", reply_markup=main_menu())
        user_data.clear()
        context.user_data.clear()
        return ConversationHandler.END

    elif text in ["Назад", "назад"]:
        print("Processing 'Назад' command")
        if current_state == ADD_NAME:
            print("Returning from ADD_NAME to main menu")
            await update.message.reply_text("Возвращаемся в главное меню.", reply_markup=main_menu())
            user_data.clear()
            return ConversationHandler.END
        elif current_state == ADD_FREQUENCY:
            print("Returning from ADD_FREQUENCY to ADD_NAME")
            await update.message.reply_text("Введите название лекарства:", reply_markup=back_menu())
            return ADD_NAME
        elif current_state == ADD_TIME:
            print("Returning from ADD_TIME to ADD_FREQUENCY")
            await update.message.reply_text("Введите количество приёмов в день (цифрой):", reply_markup=back_menu())
            user_data['times'] = []
            user_data['time_index'] = 0
            return ADD_FREQUENCY
        elif current_state == ADD_STOCK:
            print("Returning from ADD_STOCK to ADD_TIME")
            await update.message.reply_text(
                f"Введите время {user_data['time_index'] + 1}-го приёма (в формате ЧЧ:ММ):",
                reply_markup=back_menu()
            )
            user_data['times'].pop()
            user_data['time_index'] -= 1
            return ADD_TIME
        elif current_state == ADD_WARNING:
            print("Returning from ADD_WARNING to ADD_STOCK")
            await update.message.reply_text("Введите общее количество таблеток:", reply_markup=back_menu())
            return ADD_STOCK
        elif current_state == DELETE_MED:
            print("Returning from DELETE_MED to main menu")
            await update.message.reply_text("Возвращаемся в главное меню.", reply_markup=main_menu())
            return ConversationHandler.END
        elif current_state == EDIT_MED:
            print("Returning from EDIT_MED to main menu")
            await update.message.reply_text("Нет предыдущего шага, возвращаемся в главное меню.",
                                            reply_markup=main_menu())
            user_data.clear()
            context.user_data.clear()
            return ConversationHandler.END
        elif current_state == EDIT_FIELD:
            print("Returning from EDIT_FIELD to EDIT_MED")
            db = load_db()
            if not db['medicines']:
                await update.message.reply_text("Список лекарств пуст.", reply_markup=main_menu())
                user_data.clear()
                context.user_data.clear()
                return ConversationHandler.END
            keyboard = [[med['name']] for med in db['medicines']]
            await update.message.reply_text(
                "Выберите лекарство для изменения:",
                reply_markup=back_menu(keyboard)
            )
            context.user_data['current_state'] = EDIT_MED
            print(f"Switched to state EDIT_MED, current_state: {context.user_data['current_state']}")
            return EDIT_MED
        elif current_state == EDIT_NAME_VALUE:
            print("Returning from EDIT_NAME_VALUE to EDIT_FIELD")
            keyboard = [
                ['Название'],
                # ['Частота'],
                ['Время приёма'],
                ['Остаток'],
                # ['Порог предупреждения'],
                ['Добавить']
            ]
            await update.message.reply_text(
                "Выберите, что изменить:",
                reply_markup=back_menu(keyboard)
            )
            context.user_data['current_state'] = EDIT_FIELD
            print(f"Switched to state EDIT_FIELD, current_state: {context.user_data['current_state']}")
            return EDIT_FIELD
        elif current_state == EDIT_TIME:
            print("Returning from EDIT_TIME to EDIT_FIELD")
            keyboard = [
                ['Название'],
                # ['Частота'],
                ['Время приёма'],
                ['Остаток'],
                # ['Порог предупреждения'],
                ['Добавить']
            ]
            await update.message.reply_text("Выберите, что изменить:", reply_markup=back_menu(keyboard))
            context.user_data['current_state'] = EDIT_FIELD
            print(f"Switched to state EDIT_FIELD, current_state: {context.user_data['current_state']}")
            return EDIT_FIELD
        elif current_state == EDIT_STOCK:
            print("Returning from EDIT_STOCK to EDIT_FIELD")
            keyboard = [
                ['Название'],
                # ['Частота'],
                ['Время приёма'],
                ['Остаток'],
                # ['Порог предупреждения'],
                ['Добавить']
            ]
            await update.message.reply_text("Выберите, что изменить:", reply_markup=back_menu(keyboard))
            context.user_data['current_state'] = EDIT_FIELD
            print(f"Switched to state EDIT_FIELD, current_state: {context.user_data['current_state']}")
            return EDIT_FIELD
        elif current_state == EDIT_ADD_STOCK:
            print("Returning from EDIT_ADD_STOCK to EDIT_FIELD")
            keyboard = [
                ['Название'],
                # ['Частота'],
                ['Время приёма'],
                ['Остаток'],
                # ['Порог предупреждения'],
                ['Добавить']
            ]
            await update.message.reply_text("Выберите, что изменить:", reply_markup=back_menu(keyboard))
            context.user_data['current_state'] = EDIT_FIELD
            print(f"Switched to state EDIT_FIELD, current_state: {context.user_data['current_state']}")
            return EDIT_FIELD
    else:
        print(f"Navigation not handled for text: '{text}', Current state: {current_state}")
    return None


# Стартовая команда
async def start(update: Update, context):
    if not restrict_access(update, context):
        return
    await update.message.reply_text(
        "Привет! Я бот для напоминания о лекарствах. Выбери действие:",
        reply_markup=main_menu()
    )


# --- Добавление лекарства ---
async def add_medicine(update: Update, context):
    if not restrict_access(update, context):
        return ConversationHandler.END
    await update.message.reply_text(
        "Введите название лекарства:",
        reply_markup=back_menu()
    )
    context.user_data['current_state'] = ADD_NAME
    print(f"Entered state ADD_NAME, current_state: {context.user_data['current_state']}")
    return ADD_NAME


async def add_name(update: Update, context):
    user_data['name'] = update.message.text
    await update.message.reply_text(
        "Введите количество приёмов в день (цифрой):",
        reply_markup=back_menu()
    )
    context.user_data['current_state'] = ADD_FREQUENCY
    print(f"Entered state ADD_FREQUENCY, current_state: {context.user_data['current_state']}")
    return ADD_FREQUENCY


async def add_frequency(update: Update, context):
    try:
        freq = int(update.message.text)
        if freq <= 0:
            raise ValueError
        user_data['frequency'] = freq
        user_data['times'] = []
        user_data['time_index'] = 0
        await update.message.reply_text(
            f"Введите время {user_data['time_index'] + 1}-го приёма (в формате ЧЧ:ММ):",
            reply_markup=back_menu()
        )
        context.user_data['current_state'] = ADD_TIME
        print(f"Entered state ADD_TIME, current_state: {context.user_data['current_state']}")
        return ADD_TIME
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректное число.",
            reply_markup=back_menu()
        )
        return ADD_FREQUENCY


async def add_time(update: Update, context):
    time_str = update.message.text
    if not validate_time(time_str):
        await update.message.reply_text(
            "Пожалуйста, введите время в формате ЧЧ:ММ.",
            reply_markup=back_menu()
        )
        return ADD_TIME
    user_data['times'].append(time_str)
    user_data['time_index'] += 1
    if user_data['time_index'] < user_data['frequency']:
        await update.message.reply_text(
            f"Введите время {user_data['time_index'] + 1}-го приёма (в формате ЧЧ:ММ):",
            reply_markup=back_menu()
        )
        return ADD_TIME
    await update.message.reply_text(
        "Введите общее количество таблеток:",
        reply_markup=back_menu()
    )
    context.user_data['current_state'] = ADD_STOCK
    print(f"Entered state ADD_STOCK, current_state: {context.user_data['current_state']}")
    return ADD_STOCK


async def add_stock(update: Update, context):
    try:
        stock = int(update.message.text)
        if stock < 0:
            raise ValueError
        user_data['stock'] = stock
        await update.message.reply_text(
            "Введите, при каком остатке уведомлять о заканчивающихся таблетках:",
            reply_markup=back_menu()
        )
        context.user_data['current_state'] = ADD_WARNING
        print(f"Entered state ADD_WARNING, current_state: {context.user_data['current_state']}")
        return ADD_WARNING
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректное число.",
            reply_markup=back_menu()
        )
        return ADD_STOCK


async def add_warning(update: Update, context):
    try:
        warning = int(update.message.text)
        if warning < 0:
            raise ValueError
        user_data['warning'] = warning
        db = load_db()
        db['medicines'].append({
            'name': user_data['name'],
            'dose': 1,
            'frequency': user_data['frequency'],
            'times': user_data['times'],
            'stock': user_data['stock'],
            'warning': user_data['warning']
        })
        save_db(db)

        schedule_notifications(context.job_queue, user_data['name'], user_data['times'])
        await update.message.reply_text(
            "Лекарство успешно добавлено!",
            reply_markup=main_menu()
        )
        user_data.clear()
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректное число.",
            reply_markup=back_menu()
        )
        return ADD_WARNING


# --- Просмотр лекарств ---
async def view_medicines(update: Update, context):
    if not restrict_access(update, context):
        return
    db = load_db()
    if not db['medicines']:
        await update.message.reply_text("Список лекарств пуст.", reply_markup=main_menu())
        return
    for med in db['medicines']:
        text = (f"Название: {med['name']}\n"
                f"Приёмов в день: {med['frequency']}\n"
                f"Время приёма: {', '.join(med['times'])}\n"
                f"Остаток: {med['stock']}\n"
                f"Предупреждать при остатке: {med['warning']}")
        await update.message.reply_text(text, reply_markup=main_menu())


# --- Удаление лекарства ---
async def delete_medicine(update: Update, context):
    if not restrict_access(update, context):
        return ConversationHandler.END
    db = load_db()
    if not db['medicines']:
        await update.message.reply_text("Список лекарств пуст.", reply_markup=main_menu())
        return ConversationHandler.END
    keyboard = [[med['name']] for med in db['medicines']]
    await update.message.reply_text(
        "Выберите лекарство для удаления:",
        reply_markup=back_menu(keyboard)
    )
    context.user_data['current_state'] = DELETE_MED
    print(f"Entered state DELETE_MED, current_state: {context.user_data['current_state']}")
    return DELETE_MED


async def delete_medicine_confirm(update: Update, context):
    med_name = update.message.text
    db = load_db()
    db['medicines'] = [med for med in db['medicines'] if med['name'] != med_name]
    save_db(db)
    for job in context.job_queue.jobs():
        if med_name in job.name:
            job.schedule_removal()
    await update.message.reply_text(
        f"Лекарство {med_name} удалено.",
        reply_markup=main_menu()
    )
    context.user_data.clear()
    return ConversationHandler.END


# --- Изменение лекарства ---
async def edit_medicine(update: Update, context):
    if not restrict_access(update, context):
        return ConversationHandler.END
    db = load_db()
    if not db['medicines']:
        await update.message.reply_text("Список лекарств пуст.", reply_markup=main_menu())
        return ConversationHandler.END
    keyboard = [[med['name']] for med in db['medicines']]
    await update.message.reply_text(
        "Выберите лекарство для изменения:",
        reply_markup=back_menu(keyboard)
    )
    context.user_data['current_state'] = EDIT_MED
    print(f"Entered state EDIT_MED, current_state: {context.user_data['current_state']}")
    return EDIT_MED


async def edit_medicine_field(update: Update, context):
    med_name = update.message.text
    print(f"Selected medicine: {med_name}, Current state: {context.user_data['current_state']}")
    user_data['med_name'] = med_name
    keyboard = [
        ['Название'],
        # ['Частота'],
        ['Время приёма'],
        ['Остаток'],
        # ['Порог предупреждения'],
        ['Добавить']
    ]
    await update.message.reply_text(
        "Выберите, что изменить:",
        reply_markup=back_menu(keyboard)
    )
    context.user_data['current_state'] = EDIT_FIELD
    print(f"Entered state EDIT_FIELD, current_state: {context.user_data['current_state']}")
    return EDIT_FIELD


async def edit_field(update: Update, context):
    field = update.message.text
    user_data['field'] = field
    if field == "Название":
        await update.message.reply_text(
            "Введите новое название:",
            reply_markup=back_menu()
        )
        context.user_data['current_state'] = EDIT_NAME_VALUE
        print(f"Entered state EDIT_NAME_VALUE, current_state: {context.user_data['current_state']}")
        return EDIT_NAME_VALUE
    elif field == "Частота":
        await update.message.reply_text(
            "Введите новое количество приёмов в день (цифрой):",
            reply_markup=back_menu()
        )
        return EDIT_FIELD
    elif field == "Время приёма":
        db = load_db()
        for med in db['medicines']:
            if med['name'] == user_data['med_name']:
                user_data['frequency'] = med['frequency']
                user_data['times'] = []
                user_data['time_index'] = 0
                await update.message.reply_text(
                    f"Введите время {user_data['time_index'] + 1}-го приёма (в формате ЧЧ:ММ):",
                    reply_markup=back_menu()
                )
                context.user_data['current_state'] = EDIT_TIME
                print(f"Entered state EDIT_TIME, current_state: {context.user_data['current_state']}")
                return EDIT_TIME
    elif field == "Остаток":
        await update.message.reply_text(
            "Введите новое количество таблеток:",
            reply_markup=back_menu()
        )
        context.user_data['current_state'] = EDIT_STOCK
        print(f"Entered state EDIT_STOCK, current_state: {context.user_data['current_state']}")
        return EDIT_STOCK
    elif field == "Порог предупреждения":
        await update.message.reply_text(
            "Введите новый порог предупреждения:",
            reply_markup=back_menu()
        )
        return EDIT_FIELD
    elif field == "Добавить":
        await update.message.reply_text(
            "Введите количество таблеток, которое нужно добавить:",
            reply_markup=back_menu()
        )
        context.user_data['current_state'] = EDIT_ADD_STOCK
        print(f"Entered state EDIT_ADD_STOCK, current_state: {context.user_data['current_state']}")
        return EDIT_ADD_STOCK


async def edit_name_value(update: Update, context):
    value = update.message.text
    print(f"Received new name: {value}, Medicine: {user_data['med_name']}")  # Отладка
    db = load_db()
    print(f"Before update - Medicines in DB: {db['medicines']}")  # Отладка: база до изменений
    for med in db['medicines']:
        if med['name'] == user_data['med_name']:
            old_name = med['name']
            med['name'] = value
            print(f"Updated name from {old_name} to {med['name']}")  # Отладка: подтверждение изменения
            # Обновляем уведомления с новым именем
            for job in context.job_queue.jobs():
                if old_name in job.name:
                    print(f"Removing job: {job.name}")  # Отладка
                    job.schedule_removal()
            schedule_notifications(context.job_queue, med['name'], med['times'])
            await update.message.reply_text(
                f"Название обновлено на {value}.",
                reply_markup=main_menu()
            )
            break
    print(f"After update - Medicines in DB: {db['medicines']}")
    save_db(db)
    print("Saved DB after update")
    user_data.clear()
    context.user_data.clear()
    return ConversationHandler.END


async def edit_field_value(update: Update, context):
    field = user_data['field']
    value = update.message.text
    print(f"Updating field: {field}, New value: {value}, Medicine: {user_data['med_name']}")
    db = load_db()
    print(f"Before update - Medicines in DB: {db['medicines']}")
    for med in db['medicines']:
        if med['name'] == user_data['med_name']:
            if field == "Частота":
                med['frequency'] = int(value)
                med['times'] = []
                user_data['frequency'] = med['frequency']
                user_data['times'] = []
                user_data['time_index'] = 0
                await update.message.reply_text(
                    f"Введите время {user_data['time_index'] + 1}-го приёма (в формате ЧЧ:ММ):",
                    reply_markup=back_menu()
                )
                save_db(db)
                context.user_data['current_state'] = EDIT_TIME
                return EDIT_TIME
            elif field == "Порог предупреждения":
                med['warning'] = int(value)
                await update.message.reply_text(
                    f"Порог предупреждения обновлён на {value}.",
                    reply_markup=main_menu()
                )
    print(f"After update - Medicines in DB: {db['medicines']}")
    save_db(db)
    print("Saved DB after update")
    user_data.clear()
    context.user_data.clear()
    return ConversationHandler.END


async def edit_time(update: Update, context):
    time_str = update.message.text
    if not validate_time(time_str):
        await update.message.reply_text(
            "Пожалуйста, введите время в формате ЧЧ:ММ.",
            reply_markup=back_menu()
        )
        return EDIT_TIME
    user_data['times'].append(time_str)
    user_data['time_index'] += 1
    if user_data['time_index'] < user_data['frequency']:
        await update.message.reply_text(
            f"Введите время {user_data['time_index'] + 1}-го приёма (в формате ЧЧ:ММ):",
            reply_markup=back_menu()
        )
        return EDIT_TIME

    db = load_db()
    for med in db['medicines']:
        if med['name'] == user_data['med_name']:
            for job in context.job_queue.jobs():
                if med['name'] in job.name:
                    job.schedule_removal()
            med['times'] = user_data['times']
            schedule_notifications(context.job_queue, med['name'], med['times'])
    save_db(db)
    await update.message.reply_text(
        "Время приёма обновлено.",
        reply_markup=main_menu()
    )
    user_data.clear()
    context.user_data.clear()
    return ConversationHandler.END


async def edit_stock_value(update: Update, context):
    try:
        stock = int(update.message.text)
        if stock < 0:
            raise ValueError
        db = load_db()
        for med in db['medicines']:
            if med['name'] == user_data['med_name']:
                med['stock'] = stock
        save_db(db)
        await update.message.reply_text(
            "Остаток обновлён.",
            reply_markup=main_menu()
        )
        user_data.clear()
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректное число.",
            reply_markup=back_menu()
        )
        return EDIT_STOCK


async def edit_add_stock(update: Update, context):
    try:
        add_stock = int(update.message.text)
        if add_stock < 0:
            raise ValueError
        db = load_db()
        print(f"Before adding stock - Medicines in DB: {db['medicines']}")
        for med in db['medicines']:
            if med['name'] == user_data['med_name']:
                old_stock = med['stock']
                med['stock'] += add_stock
                print(f"Added {add_stock} to stock for {med['name']}. New stock: {med['stock']}")
                break
        print(f"After adding stock - Medicines in DB: {db['medicines']}")
        save_db(db)
        await update.message.reply_text(
            f"Добавлено {add_stock} таблеток. Новый остаток: {med['stock']}.",
            reply_markup=main_menu()
        )
        user_data.clear()
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректное число.",
            reply_markup=back_menu()
        )
        return EDIT_ADD_STOCK


# --- Планирование уведомлений ---
def schedule_notifications(job_queue, med_name, times):
    for time_str in times:
        hour, minute = map(int, time_str.split(':'))
        job_queue.run_daily(
            callback=send_reminder,
            time=time(hour=hour, minute=minute, tzinfo=MOSCOW_TZ),
            data={'med_name': med_name},
            name=f"{med_name}_{time_str}"
        )


async def send_reminder(context):
    job = context.job
    med_name = job.data['med_name']
    db = load_db()
    for med in db['medicines']:
        if med['name'] == med_name:
            await context.bot.send_message(
                chat_id=USER_ID,
                text=f"Пора принять {med_name}! Дозировка: {med['dose']} таблетка.",
                reply_markup=confirm_menu(med_name)
            )
            if med['stock'] <= med['warning']:
                await context.bot.send_message(
                    chat_id=USER_ID,
                    text=f"Внимание! {med_name} заканчивается. Остаток: {med['stock']}."
                )
            break


# --- Подтверждение приёма ---
async def confirm_medicine(update: Update, context):
    query = update.callback_query
    await query.answer()
    med_name = query.data.split('_')[1]
    stock = update_stock(med_name, 1)
    if stock is not None:
        await query.message.reply_text(f"Приём {med_name} подтверждён. Остаток: {stock}.")
    else:
        await query.message.reply_text("Ошибка: лекарство не найдено.")


# --- Основная функция ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    if app.job_queue:
        for job in app.job_queue.jobs():
            job.schedule_removal()

    db = load_db()
    for med in db['medicines']:
        schedule_notifications(app.job_queue, med['name'], med['times'])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(Regex('^Просмотреть лекарства$'), view_medicines))
    app.add_handler(CallbackQueryHandler(confirm_medicine, pattern='^confirm_'))

    add_med_handler = ConversationHandler(
        entry_points=[MessageHandler(Regex('^Добавить лекарство$'), add_medicine)],
        states={
            ADD_NAME: [MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), add_name)],
            ADD_FREQUENCY: [
                MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), add_frequency)],
            ADD_TIME: [MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), add_time)],
            ADD_STOCK: [MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), add_stock)],
            ADD_WARNING: [MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), add_warning)],
        },
        fallbacks=[
            MessageHandler(Regex('(?i)^(Назад|В главное меню)\s*$'), handle_navigation)
        ],
        allow_reentry=True
    )
    app.add_handler(add_med_handler)

    delete_med_handler = ConversationHandler(
        entry_points=[MessageHandler(Regex('^Удалить лекарство$'), delete_medicine)],
        states={
            DELETE_MED: [
                MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'),
                               delete_medicine_confirm)],
        },
        fallbacks=[
            MessageHandler(Regex('(?i)^(Назад|В главное меню)\s*$'), handle_navigation)
        ],
        allow_reentry=True
    )
    app.add_handler(delete_med_handler)

    edit_med_handler = ConversationHandler(
        entry_points=[MessageHandler(Regex('^Изменить лекарство$'), edit_medicine)],
        states={
            EDIT_MED: [
                MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), edit_medicine_field)],
            EDIT_FIELD: [MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), edit_field)],
            EDIT_NAME_VALUE: [
                MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), edit_name_value)],
            EDIT_TIME: [MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), edit_time)],
            EDIT_STOCK: [
                MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), edit_stock_value)],
            EDIT_ADD_STOCK: [
                MessageHandler(Text() & ~Regex('(?i)^(/start|/help|Назад|В главное меню)\s*$'), edit_add_stock)],
        },
        fallbacks=[
            MessageHandler(Regex('(?i)^(Назад|В главное меню)\s*$'), handle_navigation)
        ],
        allow_reentry=True
    )
    app.add_handler(edit_med_handler)

    app.run_polling()


if __name__ == '__main__':
    main()
