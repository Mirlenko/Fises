# Astykzhan Shop Web Scrapping

import numpy as np
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
import requests


# Function opening web page

def open_page(category, city_code, page_num = 1, url = 'https://astykzhan.kz/catalog/list/{}?PAGEN_1={}&city={}'):
    page_url = url.format(category, page_num, city_code)
    
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

def get_categories(link, city_code, main_page = 'https://astykzhan.kz/catalog/list/{}?city={}'):
    
    # this function returns the dictionary with categories titles (keys) and links to their pages
    
    url = main_page.format(link, city_code)
    
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

def get_categories_linked(cat_name, link, city_code, main_page = 'https://astykzhan.kz/catalog/list/{}?city={}'):
    
    # this function returns the dictionary with categories titles (keys) and links to their pages
    
    url = main_page.format(link, city_code)
    
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

def Astykzhan_scrap(city, url):

    if city == 'Astana':
        city_code = 1
    elif city == 'Kostanay':
        city_code = 2

    # 1. Scrapping four main categories:
    main_cats = get_categories('', city_code)

    # 2. Scrapping subcategories in each of four main categories:
    cats = {}
    for cat in main_cats:
        categories = get_categories(main_cats[cat], city_code)
        cats.update(categories)

        
    # In theory, we can go even deeper...

    # sub_cats = {}
    # for cat in cats:
    #     categories = get_categories(cats[cat])
    #     sub_cats.update(categories)

    # 3. Linking together categories and sub-categories

    sub_cats_linked = {}
    for cat in cats:
        categories = get_categories_linked(cat, cats[cat], city_code)
        sub_cats_linked.update(categories)

    # 4. Scrapping each sub-category one by one, however, categorize the scrapped data according to Categories (not subcategories)

    products = []
    titles = []
    prices = []
    old_prices = []
    categories = []

    for category in sub_cats_linked:
        #getting number of pages in each category
        _, num_pages = open_page(category, city_code)
        
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

    # 6. Returning the DataFrame - saving to csv can be added as well

    data = pd.DataFrame({'name':products, 'category':categories, 'price':prices})
    data['price'] = data['price'].astype(int)

    # file_name = 'Astykzhan_{}.csv'.format(city)
    # data.to_csv(file_name, index = False, encoding = 'cp1251')
    data.to_csv('Astykzhan_Astana.xlsx', index=False, encoding='cp1251')
    return data

# function sending the scrapped data via API

# def send(webstore_id):
#     # webstore_id = 1000 # for Astykzhan
#     requests.post('http://13.59.5.143:8082/webcatalogitems/excel', 'astykzhan_Astana.xls', webstore_id)
