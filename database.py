from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URL)
db = client["vc_music_bot"]

queue = db["queue"]
