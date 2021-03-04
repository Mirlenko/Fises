# Galmart Webstore Scrapping

# libraries
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import re

# constants
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}

def read_page(page_num, url = 'https://store.galmart.kz/shop/page'):
    page_url = url + '/' + str(page_num)
    return requests.get(page_url, headers = headers)

# 1. Getting the number of pages to scrap:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}
    page = requests.get('https://store.galmart.kz/shop/page/2', headers = headers)
    pages = []
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        content = soup.find('div', class_ = 'ast-woocommerce-container').find(class_ = 'page-numbers').text
        string = content.split('\n')
        for i in string:
            if i.isdigit():
                pages.append(int(i))
        num_pages = max(pages)