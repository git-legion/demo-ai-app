import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("APP_USERNAME")
PASSWORD = os.getenv("APP_PASSWORD")

def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

