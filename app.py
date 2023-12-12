from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from routes import api_routes

app.register_blueprint(api_routes)

if __name__ == "__main__":
    app.run()
