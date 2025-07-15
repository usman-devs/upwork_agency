from flask import redirect, url_for
from app import create_app
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
 
SECRET_KEY = os.getenv('SECRET_KEY', None)

app = create_app()

if __name__ == '__main__':
    app.run(host="localhost", port=os.getenv('APP_PORT'),debug=True)