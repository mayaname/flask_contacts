"""
Program: __init__
Author: Maya Name
Creation Date: 05/29/2025
Revision Date: 
Description: Init for Flask application


Revisions:

"""


import json
from flask import Flask
from app.extensions import db
from app.models import Employee
from app.routes import pages

def create_app(database_uri='sqlite:///app.db'):
    app = Flask(__name__)

    # Sets config for development
    app.config['SECRET_KEY'] = 'employee_directory_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    # Initialize extensions
    db.init_app(app)
 
    # Register blueprints
    app.register_blueprint(pages)

    return app