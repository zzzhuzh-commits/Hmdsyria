from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URL)
db = client["vc_ultra_bot"]

queue = db["queue"]
state = db["state"]
sudo = db["sudo"]
