from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from handlers import fetch_products
from utils.get_products import get_products

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    temp_message = context.user_data.get('temp_message')  # Получаем текущее сообщение
    
    selected_word = query.data
    product_list = get_products()

    if selected_word == 'back':
        fetch_products(update, context)
        return

    if not product_list:
        temp_message.edit_text('Не удалось получить данные с сайта.')
        return

    filtered_products = [product for product in product_list if product[0] == selected_word]

    if filtered_products:
        # Создаем клавиатуру для товаров в выбранной категории
        keyboard = [[InlineKeyboardButton(f"{name} - {stock} - {price}₽", callback_data=name)]
                    for name, stock, price in filtered_products]
        
        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton("Назад", callback_data='back')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Редактируем сообщение
        temp_message.edit_text(f"Товары в категории {selected_word}:", reply_markup=reply_markup)
        context.user_data['temp_message'] = temp_message  # Обновляем сообщение в context.user_data
    else:
        temp_message.edit_text(f"В категории {selected_word} нет товаров.")
