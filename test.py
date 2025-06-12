import pymongo
import certifi
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

username = quote_plus(os.getenv("MON_MAIL"))
password = quote_plus(os.getenv("MON_PASS"))

uri = f"mongodb+srv://{username}:{password}@cluster0.cpdb7m9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = pymongo.MongoClient(uri, tls=True, tlsCAFile=certifi.where())
    print("Pinging MongoDB...")
    client.admin.command('ping')
    print("✅ MongoDB Atlas connection successful!")
except Exception as e:
    print("❌ Connection failed:", e)