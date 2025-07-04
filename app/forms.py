"""
Program: Forms
Author: Maya Name
Creation Date: 06/08/2025
Revision Date: 
Description: Forms for Flask application


Revisions:

"""

from flask_wtf import FlaskForm
from wtforms import (SelectField, 
                     StringField, 
                     SubmitField)
from wtforms.validators import InputRequired, Length, Regexp

department = [('ENG', 'Engineering'),
              ('HR', 'Human Resources'),
              ('IT', 'Information Technology'),
              ('MAN', 'Manufacturing'),
              ("SAL", 'Sales'),
         ]

class AddEmployeeForm(FlaskForm):

    fname = StringField("First Name", validators=[InputRequired()])
    lname = StringField("Last Name", validators=[InputRequired()])
    dept = SelectField('Department', choices=department, 
                       validators=[InputRequired()])
    ext = StringField("Extension", validators=[InputRequired(),
                                               Length(min=4, max=4, 
                                                      message='Extension must be between 4 numbers long'),
                                               Regexp(regex='^[0-9]+$', 
                                                      message='Only numeric characters are allowed.')])
    submit = SubmitField("Add Employee")

class UpdateEmployeeForm(AddEmployeeForm):

    submit = SubmitField("Update Employee")