from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort
from Galmart_Scrapping import Galmart_scrap
from Astykzhan_Scrapping import Astykzhan_scrap
from Categorization_Model import categorize

app = Flask(__name__)
api = Api(app)

class Scrapping_Service(Resource):
    def get(self, storeName, city, url):

        if storeName == 'Galmart':
            print('Galmart scrapping...')

            #firstly scrapping
            data_Galmart = Galmart_scrap(city, url)

            # categories missing - using Categorization Model
            categorize(data_Galmart)
            return data_Galmart.to_json()

        elif storeName == 'Astykzhan':
            print('Astykzhan scrapping...')
            data_Astykzhan = Astykzhan_scrap(city, url)
            return data_Astykzhan.to_json()
        # more conditions can be added in case additional stores scrapping

# class Categorization_Service(Resource):
#     def post(self, webStoreId):
#

api.add_resource(Scrapping_Service, '/scrap_csv/<string:storeName>/<string:city>/<string:url>')

if __name__ == '__main__':
    app.run(debug=True) # remove debug before deployment

###########################################################################################
# training
# from flask import Flask, request
# from flask_restful import Api, Resource, reqparse, abort
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
# api = Api(app)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # put here the name of the database
# db = SQLAlchemy(app)
#
# class VideoModel(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(100), nullable=False)
#     views = db.Column(db.Integer, nullable=False)
#     likes = db.Column(db.Integer, nullable=False)
#
#     def __repr__(self):
#         return True
#
# db.create_all()
#
# video_put_args = reqparse.RequestParser()
# video_put_args.add_argument('name', type=str, help='Video name is required', required=True)
# video_put_args.add_argument('views', type=int, help='Video views number is required', required=True)
# video_put_args.add_argument('likes', type=int, help='Video likes number is required', required=True)
#
# info = {'apple': {'price': 1.25, 'origin': 'Spain'},
#         'orange':{'price':0.96, 'origin': 'Italy'}}
#
# videos = {}
#
# def no_id(video_id):
#     if video_id not in videos:
#         abort(404, message='Video ID is not valid...')
#
# def id_exists(video_id):
#     if video_id in videos:
#         abort(409, message='Video with that ID already exists...')
#
# class HelloWorld(Resource):
#     def get(self, item):
#         return info[item]
#
# class Video(Resource):
#     def get(self, video_id):
#         no_id(video_id)
#         return videos[video_id]
#
#     def put(self, video_id):
#         id_exists(video_id)
#         args = video_put_args.parse_args()
#         videos[video_id] = args
#         return videos[video_id], 201 # 201 stands for created
#
#     def delete(self, video_id):
#         no_id(video_id)
#         del videos[video_id]
#         return '', 204
#
# api.add_resource(HelloWorld, '/helloworld/<string:item>' ) # /helloworld - end point - user call the key
#
# api.add_resource(Video, '/video/<int:video_id>' ) # /helloworld - end point - user call the key
#
# if __name__ == '__main__':
#     app.run(debug=True)

