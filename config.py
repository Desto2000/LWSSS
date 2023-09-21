from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("APIKEY")
api_url = os.getenv("APIURL")
bot_token = os.getenv("TOKEN")
