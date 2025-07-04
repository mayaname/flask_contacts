"""
Program: run.py
Author: Maya Name
Creation Date: 05/29/2025
Revision Date: 
Description: File that launches the Flask 
             Contacts application. 
             
Revisions:

"""


from app import create_app

app = create_app()


if __name__ == '__main__':
    app.run()
