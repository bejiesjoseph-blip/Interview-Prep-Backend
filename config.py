import os
from dotenv import load_dotenv
import mysql.connector
import google.generativeai as genai



load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash"
)

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
    autocommit=True
)

cursor = db.cursor(dictionary=True)