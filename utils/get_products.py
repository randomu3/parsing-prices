import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os

# Load environment variables
load_dotenv(os.path.join('config', '.env'))

SITE_URL = os.getenv('SITE_URL')

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
