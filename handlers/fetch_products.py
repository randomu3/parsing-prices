from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.get_products import get_products

def fetch_products(update: Update, context: CallbackContext):
    temp_message = context.user_data.get('temp_message')  # Получаем текущее сообщение

    if not temp_message:
        if update.message:
            temp_message = update.message.reply_text('Загрузка товаров...')
        elif update.callback_query:
            temp_message = update.callback_query.message.reply_text('Загрузка товаров...')
        else:
            return
        context.user_data['temp_message'] = temp_message  # Сохраняем сообщение в context.user_data
    
    product_list = get_products()

    if not product_list:
        temp_message.edit_text('Не удалось получить данные с сайта.')
        return

    # Получаем уникальные первые слова из названий товаров для создания категорий
    words = list(set(product[0].split(' ')[0] for product in product_list))
    
    # Создаем клавиатуру для категорий товаров
    keyboard = []
    row = []
    for word in words:
        row.append(InlineKeyboardButton(word, callback_data=word))
        if len(row) == 2:  # Добавляем кнопки попарно
            keyboard.append(row)
            row = []
    if row:  # Добавляем последний неполный ряд, если есть
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Редактируем сообщение
    temp_message.edit_text('Выберите категорию:', reply_markup=reply_markup)
    context.user_data['temp_message'] = temp_message  # Обновляем сообщение в context.user_data