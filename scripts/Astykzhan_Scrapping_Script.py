# Astykzhan Shop Web Scrapping



import numpy as np
import pandas as pd
import re
import time
import json
import ast
import argparse
from bs4 import BeautifulSoup
import requests


# Function opening web page: city_num = 1 if Astana; city_num = 2 if Kostanay.

def open_page(category, page_num = 1, city_num = 1, url = 'https://astykzhan.kz/catalog/list/{}?PAGEN_1={}&city={}'):
    page_url = url.format(category, page_num, city_num)
    
    #exceptions
    while True:
        try:
            page = requests.get(page_url)
            break
        except requests.exceptions.ConnectionError:
            print("TimeOut...Sleep")
            time.sleep(10)
            pass
        
    #getting the pages number
    if page.status_code == 200:
        pages = []
        soup = BeautifulSoup(page.text, "html.parser")
        content = soup.findAll('div', class_ = 'pagenation-elem')
        for i in content:
            if len(i.text.strip('\n')) > 0:
                pages.append(int(i.text.strip('\n')))
        if pages != []:
            num_pages = max(pages)
        else:
            num_pages = 1
            
    return page, num_pages


# Functions scrapping the categories names and links to them

def get_categories(link, main_page = 'https://astykzhan.kz/catalog/list/{}?city=1'):
    
    # this function returns the dictionary with categories titles (keys) and links to their pages
    
    url = main_page.format(link)
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    content = soup.findAll('div', class_ = 'category-elem')

    categories = {}
    for element in content:
        title = element.find('h5').text
        link = re.search('(href=)"(\S*)"', str(element))[0][20:-1]
        
        categories[title] = link
        
    return categories


# ### Linking together categories and sub-categories, related to them

def get_categories_linked(cat_name, link, main_page = 'https://astykzhan.kz/catalog/list/{}?city=1'):
    
    # this function returns the dictionary with categories titles (keys) and links to their pages
    
    url = main_page.format(link)
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    content = soup.findAll('div', class_ = 'category-elem')

    categories = {}
    for element in content:
        title = element.find('h5').text
        link = re.search('(href=)"(\S*)"', str(element))[0][20:-1]
        
        categories[link] = [cat_name, title]
        
    return categories


### MAIN 

def scrap():

    # 1. Scrapping four main categories:
    main_cats = get_categories('')

    # 2. Scrapping subcategories in each of four main categories:
    cats = {}
    for cat in main_cats:
        categories = get_categories(main_cats[cat])
        cats.update(categories)

        
    # In theory, we can go even deeper...

    # sub_cats = {}
    # for cat in cats:
    #     categories = get_categories(cats[cat])
    #     sub_cats.update(categories)

    # 3. Linking together categories and sub-categories

    sub_cats_linked = {}
    for cat in cats:
        categories = get_categories_linked(cat, cats[cat])
        sub_cats_linked.update(categories)

    # 4. Scrapping each sub-category one by one, however, categorize the scrapped data according to Categories (not subcategories)

    products = []
    titles = []
    prices = []
    old_prices = []
    categories = []

    for category in sub_cats_linked:
        #getting number of pages in each category
        _, num_pages = open_page(category)
        
        # scrapping pages in category one by one
        for i in np.arange(1, num_pages + 1):
            page, _ = open_page(category, i)
            print(sub_cats_linked[category][1], num_pages, '/', i)
            
            # scrapping itself
            if page.status_code == 200:
                soup = BeautifulSoup(page.text, "html.parser")
                content = soup.findAll('div', class_ = 'product-card-elem service_product_element')
                
                for product in content:
                    
                    #long product name
                    name = product.find('div', {'class': 'product-card-elem-name'}).text.replace('\n','')
                    # only unique names
                    if name not in products:
                        products.append(name)

                        #only title
                        title = re.findall('([A-ZА-Я]{2,}){1,}([-+,.]\d+)?', name)
                        if title is None:
                            titles.append('"None"')
                        else:
                            result = ''

                        for i in title:
                            if i[1] is None:
                                result += i[0] + ' '
                            else:
                                result += i[0] + i[1] + ' '
                        titles.append(result)

                        #product price
                        price = product.find('div', {'class': 'product-card-elem-bottom'}).find('span').text
                        prices.append(price)

                        #product old price
                        string = product.find('div', {'class': 'product-card-elem-oldprice'}).find('span')
                        if string is None:
                            old_prices.append(price)
                        else:
                            string = str(string)
                            old_price = re.search('\d+', string)
                            old_prices.append(old_price[0])

                        #category
                        categories.append(sub_cats_linked[category][0])
        
            else:
                print(page.status_code)

    # 5. Making sure the scrapped data is consistent
    print('Data consistency: ', len(products) == len(titles) == len(prices) == len(old_prices) == len(categories))


    # 6. Importing the scrapped data to Excel

    data = pd.DataFrame({'name':products, 'price':prices, 'category':categories})
    data['price'] = data['price'].astype(int)

    data.to_excel('Astykzhan_Astana.xls', index = False, header = ['name','price', 'category'], engine = 'xlsxwriter')
    print('Import to .xlsx DONE')


    # 7. Saving to csv format for further use

    data = pd.DataFrame({'name':products, 'category':categories, 'price':prices, 'old_price':old_prices, 'title':titles})
    data['price'] = data['price'].astype(int)

    data.to_csv('Astykzhan_Astana.csv', index = False, encoding = 'utf-8')
    print('Import to .csv DONE')
    print('ALL DONE')

    # THE END #


# function sending the scrapped data via API

def send(webstore_id):
    # webstore_id = 1000 # for Astykzhan
    requests.post('http://13.59.5.143:8082/webcatalogitems/excel', 'astykzhan_Astana.xls', webstore_id)


# CLI
parser = argparse.ArgumentParser(description = 'Astykzhan Webstore Products Scrapping Script')
parser.add_argument('mode', help = 'Select the mode: scrap the data or send via API. Print "scrap" or "send"', type = str)
parser.add_argument('second_arg', help = 'Please insert webstore id', type = str)
args = parser.parse_args()



if args.mode == 'scrap':
    print('Scrapping the data...')
    scrap()
elif args.mode == 'send':
    print('Sending via API...')
    send(args.second_arg)
else:
    print('Please follow the instructions provided')