from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

class ScrappingService(Resource):
    def get(self, storeName, city, url):
        if storeName == 'Galmart':
            return Galmart_scrap(city, url)
        elif storeName == 'Astykzhan':
            return Astykzhan_scrap(city, url)
        # more conditions can be added in case additional stores scrapping

api.add_resource(ScrappingService, '/ScrappingService/<string:storeName>/<string:city>/<string:url>')

if __name__ == '__main__':
    app.run(debug=True) # remove debug before deployment