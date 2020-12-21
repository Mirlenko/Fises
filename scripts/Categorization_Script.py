# FISES Classification Script
# The model is based on Google fastText framework

import numpy as np
import pandas as pd
import requests
import argparse

from nltk.tokenize import RegexpTokenizer
import pymorphy2

import fasttext


# Function tokenizing and lemmatizing the corpus

def clean_tokens(data, min_len = 2):

    tokenizer = RegexpTokenizer('[А-ЯЁа-яA-Za-z]+')
    stop_words = ['мл', 'шт', 'гр', 'кг', 'acc', 'л', 'пл', 'бут', 'карт', 'кор', 'мм', 'цв', 'х', 'б', 'р', 'арт', 'пак', \
                  'эко', 'россия', 'казахстан', 'китай', 'германия', 'италия', 'испания', 'украина', 'сша', 'ассорт']
    line = []
    final = []
    
    # lemmatization
    morph = pymorphy2.MorphAnalyzer()
    
    for row in data:
        result = tokenizer.tokenize(row)
        for element in result:
            element = element.lower()
            if (element not in stop_words) & (len(element) > min_len):
                element = element.strip()
                element = morph.parse(element)[0].normal_form
                line.append(element)

        final.append(' '.join(line))
        line = []
        
    return final

# Neural Networks - FastText

def create_corpus(data, target, file_name = 'corpus.txt'):
    corpus = []
    for prod, cat in zip(data, target):
        cat = cat.replace(', ', '-').replace(' ', '-')
        cat = '__label__' + cat
        result = cat + ' ' + prod + '\n'
        corpus.append(result)

    file = open(file_name, 'w', encoding = 'utf-8')
    file.writelines(corpus)
    file.close()


# Function making prediction based on the fastText model
def make_prediction(X_pred, model):
    y_pred = []
    for row in X_pred:
        y_pred.append(model.predict(row)[0][0].replace('__label__', '').replace('-', ' '))
        
    return pd.DataFrame({'Product':X_pred, 'Category':y_pred})




# THE END #

def main():

    # 1. Reading Astykzhan file, used for model training
    # Galmart file, used for category prediction
    astykzhan = pd.read_csv('Astykzhan_Astana.csv')
    X_train = astykzhan.name.values
    target = astykzhan.category.values

    galmart = pd.read_csv('Galmart.csv')
    X_pred = galmart.name.values

    # 2. Calling tokenization function
    X_train = clean_tokens(X_train)
    X_pred = clean_tokens(X_pred)

    # 3. Creating training corpus
    create_corpus(X_train, target, 'corpus.txt')
    print('Corpus created')

    # 4. Training the model
    # setting up both epochs and learning rate
    print('Training model...')
    model = fasttext.train_supervised('corpus.txt', epoch = 25, lr = 1)

    # 5. Making prediciton for categories
    data = make_prediction(X_pred, model)
    data['price'] = galmart.price.astype(int)

    # 6. Importing to Excel
    data.to_excel('galmart_categorized.xlsx', index = False, header = ['name','price', 'category'], engine = 'xlsxwriter')
    print('Import to .xlsx DONE')


# function sending the scrapped data via API

def send(webstore_id):
    # posting the categorized Galmart products via API:
    webstore_id = 1001 # for Galmart
    requests.post('http://13.59.5.143:8082/webcatalogitems/excel', 'galmart_categorized.xls', webstore_id)


# CLI
parser = argparse.ArgumentParser(description = 'FISES Categorization Model Script')
parser.add_argument('mode', help = 'Select the mode: predict the category or send via API. Print "predict" or "send"', type = str)
parser.add_argument('second_arg', help = 'Please insert webstore id', type = str)
args = parser.parse_args()



if args.mode == 'predict':
    print('Launching the fastText model...')
    main()
elif args.mode == 'send':
    print('Sending via API...')
    send(args.second_arg)
else:
    print('Please follow the instructions provided')
