# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource

app = Flask(__name__)
# app.config["MONGO_DBNAME"] = "tweets_db"
app.config["MONGO_URI"] = "mongodb://localhost:27017/DemoDB"
mongo = PyMongo(app)
APP_URL = "http://127.0.0.1:5000"


class Tweets(Resource):
    def get(self, id=None, range=None, emotion=None):
        data = []

        if id:
            # tweet_info = mongo.db.tweets.find_one({"id": id}, {"_id": 0})
            tweet_info = mongo.db.tweets.find({}, {"_id": 0})
            for tweet in tweet_info:
                data.append(tweet)
            if tweet_info:
                return jsonify({"status": "ok", "data": data})
            else:
                return {"response": "no tweet found for {}".format(id)}

        elif range:
            #YYYYMMDDHHMMSS
            range = range.split('to')
            cursor = mongo.db.tweets.find({"timestamp":{"$gt": int(range[0])}, "timestamp":{"$lt": int(range[1])}}, {"_id": 0}).limit(10)
            for tweet in cursor:
                tweet['url'] = APP_URL + url_for('tweets') + "/" + tweet.get('id')
                data.append(tweet)

            return jsonify({"range": range, "response": data})

        elif emotion:
            cursor = mongo.db.tweets.find({"emotion": emotion}, {"_id": 0}).limit(10)
            for tweet in cursor:
                tweet['url'] = APP_URL + url_for('tweets') + "/" + tweet.get('id')
                data.append(tweet)

            return jsonify({"emotion": emotion, "response": data})

        else:
            cursor = mongo.db.tweets.find({}, {"_id": 0, "update_time": 0}).limit(10)

            for tweet in cursor:
                # print tweet
                tweet['url'] = APP_URL + url_for('tweets') + "/" + tweet.get('id')
                data.append(tweet)

            return jsonify({"response": data})

    def post(self):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            id = data.get('id')
            if id:
                if mongo.db.tweets.find_one({"id": id}):
                    return {"response": "tweet already exists."}
                else:
                    mongo.db.tweets.insert(data)
            else:
                return {"response": "id number missing"}

        return redirect(url_for("tweets"))

    def put(self, id):
        data = request.get_json()
        mongo.db.tweets.update({'id': id}, {'$set': data})
        return redirect(url_for("tweets"))

    def delete(self, id):
        mongo.db.tweets.remove({'id': id})
        return redirect(url_for("tweets"))


class Index(Resource):
    def get(self):
        return redirect(url_for("tweets"))

class CheckMongo(Resource):
    def get(self):
        try:
            # Kiểm tra kết nối bằng cách truy vấn danh sách các cơ sở dữ liệu
            db_names = mongo.cx.list_database_names()
            collections = mongo.db.list_collection_names()
            return jsonify({"status": "Connected", "databases": db_names, "collections": collections})
        except Exception as e:
            return jsonify({"status": "Connection failed", "error": str(e)})
        

api = Api(app)
api.add_resource(CheckMongo, "/check_mongo", endpoint="check_mongo")
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Tweets, "/api", endpoint="tweets")
api.add_resource(Tweets, "/api/<string:id>", endpoint="id")
api.add_resource(Tweets, "/api/emotion/<string:emotion>", endpoint="emotion")
api.add_resource(Tweets, "/api/range/<string:range>", endpoint="range")

if __name__ == "__main__":
    app.run(debug=True)