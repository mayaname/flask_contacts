"""
Program: Routes
Author: Maya Name
Creation Date: 03/05/2025
Revision Date: 
Description: Routes file for Flask application


Revisions:

"""


from flask import (Blueprint,  
                   flash, 
                   render_template, 
                   redirect, 
                   request, 
                   url_for)
from app.extensions import db
from app.forms import AddEmployeeForm, UpdateEmployeeForm
from app.models import Employee


pages = Blueprint('pages', __name__)

@pages.route('/')
@pages.route('/index/')
def index():
    head_title = 'Home'
    page_title = 'Employees'
    page = request.args.get('page', default=1, type=int) 
    rows_per_page = 3 

    try:
        emps_paginated = Employee.query.order_by(Employee.lname.asc()) \
            .paginate(page=page, per_page=rows_per_page, error_out=False)
    except Exception as e:
        flash(f'Database error: \n{e}', 'error')

    return render_template(
        'index.html',
        head_title=head_title,
        page_title=page_title,
        emps=emps_paginated.items, 
        current_page=page,
        total_pages=emps_paginated.pages
    )

@pages.route('/add_emp/', methods=['GET', 'POST'])
def add_emp(): 
    head_title = 'Add'
    page_title = 'Add Employee'
    form = AddEmployeeForm() 

    if form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        dept = form.dept.data
        ext = form.ext.data
        email = f'{fname.lower()}_{lname.lower()}@abnor.com'
        emps = Employee(fname=fname,
                            lname=lname,
                            dept=dept,
                            ext=ext,
                            email=email
                            )
        try:    
            db.session.add(emps)
            db.session.commit()
            flash(f'{emps.fname} {emps.lname} added to database', 'success')
            return redirect(url_for('pages.index')) 
        except Exception as e:
            db.session.rollback() 
            flash(f'Database error: \n{e}', 'error')
        finally:
            db.session.close()  
    
    return render_template('add_emp.html',
                    head_title=head_title,
                    page_title=page_title,
                    form=form)

@pages.route('/delete_emp/<int:emp_id>/', methods=['GET', 'POST'])
def delete_emp(emp_id):

    try:
        emp = Employee.query.get_or_404(emp_id)

        if emp:
            db.session.delete(emp)
            db.session.commit()
            flash(f'{emp.fname} {emp.lname} deleted from database', 'success')
        else:
            flash(f"Employee {emp.fname} {emp.lname} not found.", category="error")         
    except Exception as e:
            db.session.rollback()
            flash(f'Database error: \n{e}', 'error')
    finally:
            db.session.close()        
    return redirect(url_for('pages.index'))

@pages.route('/update_emp/<int:emp_id>/', methods=['GET', 'POST'])
def update_emp(emp_id):
    head_title = 'Update'
    page_title = 'Update Employee'
    
    emp = Employee.query.get_or_404(emp_id)

    form = UpdateEmployeeForm(obj=emp)

    if form.validate_on_submit():
        try:
            emp.fname = form.fname.data
            emp.lname = form.lname.data
            emp.dept = form.dept.data
            emp.ext = form.ext.data
            db.session.commit()
            flash(f'{emp.fname} {emp.lname} updated in database', 'success')
            return redirect(url_for('pages.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Database error: \n{e}', 'error')
        finally:
            db.session.close()

    return render_template('update_emp.html',
                           head_title=head_title,
                           page_title=page_title,
                           form=form,
                           emp=emp)