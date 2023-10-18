import os
from dotenv import load_dotenv
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, Updater, CallbackQueryHandler
from bs4 import BeautifulSoup
import requests

# Загрузка переменных окружения из .env файла
load_dotenv(os.path.join('config', '.env'))

# Получение токена бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SITE_URL = os.getenv('SITE_URL')

# Инициализация бота и обработчиков
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я ваш бот для покупок.')
    
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

def get_products():
    response = requests.get(SITE_URL)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('tr', {'data-id': True})
    product_list = []

    for product in products:
        name_div = product.find('div', class_='title')
        stock_td = name_div.find_parent('td').find_next_sibling('td') if name_div else None
        price_span = product.find('span', class_='price_tbl')

        if name_div and stock_td and price_span:
            name = name_div.text.strip().split(' ')[0]  # Берем только первое слово
            stock = stock_td.text.strip()
            price = price_span.text.strip()
            product_list.append((name, stock, price))
    
    return product_list

# Добавление обработчиков команд
start_handler = CommandHandler('start', start)
fetch_handler = CommandHandler('fetch', fetch_products)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(fetch_handler)
dispatcher.add_handler(CallbackQueryHandler(button))

# Запуск бота
updater.start_polling()
