"""
Program: Conftest.py
Author: Maya Name
Creation Date: 07/15/2025
Revision Date: 
Description: Configuration for pytest in Flask application
https://www.youtube.com/watch?v=RLKW7ZMJOf4

Revisions:

"""


import pytest

from app import create_app, db
from app.models import Employee

@pytest.fixture(scope='session')
def app():
    """Create a Flask application for the tests."""
    app = create_app(database_uri='sqlite:///:memory:')
    # Disable CSRF for form submissions
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
    yield app
    # Teardown after test session
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def populate_db(app):
    """Populate the database with sample data before each test."""
    with app.app_context():
        # Per-Test Cleanup
        db.session.query(Employee).delete()
        
        # Create sample employees (Maya must be the first employee)
        employees = [
            Employee(id=1, fname='Maya', lname='Name', dept='IT', ext='3234', email='maya_name@adnor.com'),
            Employee(id=2, fname='Gil', lname='Flangeworm', dept='HR', ext='1234', email='gil_flangeworm@abnor.com'),
            Employee(id=3, fname='Wil', lname='Manglefrog', dept='Sales', ext='2234', email='wil_manglefrogl@abnor.com')
        ]
        
        db.session.add_all(employees)
        db.session.commit()
    yield

@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()