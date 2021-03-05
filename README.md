# FISES

In the current repository the microservices scripts are contained. 
For the moment, two services are provided:
* Scrapping service
* Categorization service

As their names suggest, the Scrapping Service is used to parse products data (product name, price, category, origin etc) from supermarkets websites ([ _Astykzhan_](https://astykzhan.kz/?city=1) and [_Galmart_](https://galmart.kz/)). Unfortunately, these resources does not provide API; for this reason, `BeautifulSoup` library is used to scrap the data directly from the pages. 

The Categorization Service is used to determine the category of each product for supermarkets, where this feature cannot be scrapped directly from the website (e.g. Galmart). The Categorization Model is based on the `fastText` library. For text tokenization the `nltk` platform is used, the lemmatization procedure is implemented via the `pymorphy2` morphological analyzer. 

The REST API architecture (`Flask`) is used to ensure link between the services, that are going to be connected to Android and IOS applications.

As the services are under development, no help is provided yet.
