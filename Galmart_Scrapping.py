# # Galmart Shop Web Scrapping

from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import re


# Function opening web page:
def open_page(page_num, url = 'https://store.galmart.kz/shop/page'):
    head = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}
    page_url = url + '/' + str(page_num)
    return requests.get(page_url, headers = head)


# Main Function
def Galmart_scrap(city, url):

    # 1. Getting the number of pages to scrap:
    head = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}
    page = requests.get('https://store.galmart.kz/shop/page/2', headers = head)
    pages = []
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        content = soup.find('div', class_ = 'ast-woocommerce-container').find(class_ = 'page-numbers').text
        string = content.split('\n')
        for i in string:
            if i.isdigit():
                pages.append(int(i))
        num_pages = max(pages)


    # 2. Reading the shop pages one by one. 
    products = []
    prices = []
    for i in np.arange(1,num_pages+1):
        page = open_page(i)
        print(num_pages, '/', i)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")
            content = soup.findAll('div', class_ = 'astra-shop-summary-wrap')
            for product in content:
                if product.find(class_='woocommerce-loop-product__title') is not None:
                    products.append(product.find('h2').text)
                    if product.find('span', class_='woocommerce-Price-amount amount') is not None:
                        prices.append(product.find('span', class_='woocommerce-Price-amount amount').text)
                    else:
                        prices.append(0)
        else:
            print(page.status_code)


    # 3. Deleting irrelevant symbols from the price:
    prices_clean = []
    pattern = '(\d+[,])?\d+'
    for price in prices:
        price = str(price).replace(',','')
        string = re.search(pattern, str(price))
        prices_clean.append(string[0])


    # 4. Taking only relevant information from the product description:
    # Comment out if product origin is useless
    origins = []
    for product in products:
        separated = str(product).strip().split(',')
        if len(separated) > 1:
            string = str(product).strip().split(' ')
            if string[-1].istitle():
                origins.append(string[-1].strip()) 
            elif string[-2].istitle():
                origins.append(string[-2].strip()) 
            else:
                origins.append('NONE')
        else:
            origins.append('NONE')

    # 5. Returning the DataFrame - saving to csv can be added as well
    data = pd.DataFrame({'name':products, 'price':prices_clean})
    data['price'] = data['price'].astype(int)
    # print('Ready to save to .csv format...')
    file_name = 'Galmart_{}_raw.csv'.format(city)
    data.to_csv(file_name, index=False, encoding='cp1251')
    return data
