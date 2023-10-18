import os
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import CommandHandler, CallbackContext, Updater
from bs4 import BeautifulSoup
import requests

# Загрузка переменных окружения из .env файла
load_dotenv(os.path.join('config', '.env'))

# Получение токена бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализация бота и обработчиков
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я ваш бот для покупок.')

def fetch_products(update: Update, context: CallbackContext):
    response = requests.get('https://lightshop.su/')
    if response.status_code != 200:
        update.message.reply_text('Не удалось получить данные с сайта.')
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('tr', {'data-id': True})

    for product in products:
        name_div = product.find('div', class_='title')
        price_span = product.find('span', class_='price_tbl')

        # Используем метод find_next_sibling для поиска следующего <td>
        stock_td = name_div.find_parent('td').find_next_sibling('td') if name_div else None

        # Если не удается получить какую-либо информацию, пропускаем этот товар
        if not (name_div and stock_td and price_span):
            print(f"Debug info: name_div={name_div}, stock_td={stock_td}, price_span={price_span}")
            continue

        name = name_div.text.strip()
        stock = stock_td.text.strip() if stock_td else 'Неизвестно'
        price = price_span.text.strip()
        
        update.message.reply_text(f"{name} - {stock} - {price}₽")

# Добавление обработчиков команд
start_handler = CommandHandler('start', start)
fetch_handler = CommandHandler('fetch', fetch_products)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(fetch_handler)

# Запуск бота
updater.start_polling()
