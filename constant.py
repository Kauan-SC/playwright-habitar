import os

from dotenv import load_dotenv

load_dotenv()

link = os.environ.get("URL")
email = os.environ.get("EMAIL")
password = os.environ.get("SENHA")

# Gmail API (OAuth)
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("SECRET_KEYS")
# Filtro opcional para achar o e-mail do código (sintaxe de busca do Gmail)
gmail_query = os.environ.get("GMAIL_QUERY", "newer_than:1d")
