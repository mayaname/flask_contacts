# Flask Employee Directory

This is a bare-bones Flask Employee Directory CRUD application that uses SQLite3 and Flask-SQLAlchemy for data management. There is no user authentication. Form processing is done with Flask-WTF and traditional HTML form tags. The app only uses the default browser styles. Did I mention that this was a bare-bones app!

## Setup

### Create Virtual Environment

```bash
 python3 -m venv venv
```

### Install Dependence

```bash
 pip install -r requirements.txt 
```

### Using Sample Data

You can use manage.db to create and populate the database with sample employee contact data from the employees.cvs file. 

### Unit Testing

I updated the app to add unit testing using pytest and BeautifulSoup. I did not find a lot of info on unit testing Flask app, so here are the references I used:

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [pytest](https://docs.pytest.org/en/stable/)
- [Getting Started With Testing in Flask](https://www.youtube.com/watch?v=RLKW7ZMJOf4)
