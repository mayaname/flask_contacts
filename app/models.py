"""
Program: Models
Author: Maya Name
Creation Date: 05/29/2025
Revision Date: 
Description: Models for Flask application


Revisions:

"""


import sqlalchemy as sa
import sqlalchemy.orm as so
from .extensions import db 


class Employee(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    fname: so.Mapped[str] = so.mapped_column(sa.String(20))
    lname: so.Mapped[str] = so.mapped_column(sa.String(20))
    dept: so.Mapped[str] = so.mapped_column(sa.String(20))
    ext: so.Mapped[str] = so.mapped_column(sa.String(4))
    email: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, unique=True)
