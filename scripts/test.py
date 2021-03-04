import requests

BASE = 'http://127.0.0.1:5000/'
storeName = 'Galmart'
city = 'Astana'
url = 'url'

get_response = requests.get(BASE + 'scrap_csv/' + storeName + '/' + city + '/' + url)
print(get_response.json())

webStoreId = 1001 # Galmart
post_response = requests.post(BASE + 'categorize/' + webStoreId)
print(post_response)