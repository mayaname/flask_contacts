"""
Program: Test_app.py
Author: Maya Name
Creation Date: 07/15/2025
Revision Date: 
Description: Unit tests for the Flask application


Revisions:

"""


from bs4 import BeautifulSoup
from app.models import Employee


def test_index_route_loads_correctly(client):
    response = client.get('/')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser') 
    assert soup.title.string == 'Home - Contacts', "'index.html' page not loaded"

def test_index_route_displays_employee_data (client):
    response = client.get('/')
    soup = BeautifulSoup(response.data, 'html.parser')  

    gil_cell = soup.find('td', string='Gil')
    assert gil_cell is not None, "Employee 'Gil' not found in table"
    
    row = gil_cell.find_parent('tr')
    
    last_name_link = row.find('a', string=lambda s: s and s.strip() == 'Flangeworm')
    assert last_name_link is not None, "Last name 'Flangeworm' not found in row"
    
    dept_cell = row.find('td', string='HR')
    assert dept_cell is not None, "Department 'HR' not found in row" 

    ext_cell = row.find('td', string='1234')
    assert ext_cell is not None, "Extension '1234' not found in row"

    email_cell = row.find('td', string='gil_flangeworm@abnor.com')
    assert email_cell is not None, "Email 'gil_flangeworm@abnor.com' not found in row"     

def test_add_route(client):
    response = client.get('/add_emp/')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser') 
    assert soup.title.string == 'Add - Contacts', "'add_emp.html' page not loaded" 

def test_add_employee(client, app):
    # New employee data
    data = {
        'fname': 'Megan',
        'lname': 'Wolfgrill',
        'dept': 'IT',
        'ext': '3999'
    }
    
    response = client.post('/add_emp/', data=data, follow_redirects=True)
    
    # Verify successful processing and redirect
    assert response.status_code == 200
    assert b'Megan Wolfgrill added to database' in response.data
    
    # Check database for new employee
    with app.app_context():
        emp = Employee.query.filter_by(fname='Megan', lname='Wolfgrill').first()
        
        assert emp is not None
        assert emp.dept == 'IT'
        assert emp.ext == '3999'
        assert emp.email == 'megan_wolfgrill@abnor.com'

    # Navigate to last page where the new employee should appear
    total_employees = 4
    per_page = 3
    last_page = (total_employees - 1) // per_page + 1

    response = client.get(f'/?page={last_page}')
    assert response.status_code == 200
    
    # Verify new employee appears in the table
    soup = BeautifulSoup(response.data, 'html.parser')
    megan_cell = soup.find('td', string=lambda s: s and s.strip() == 'Megan')
    assert megan_cell is not None, "Employee 'Megan' not found in table"
    
    megan_row = megan_cell.find_parent('tr')
    assert megan_row.find('a', string=lambda s: s and s.strip() == 'Wolfgrill') is not None
    assert megan_row.find('td', string=lambda s: s and s.strip() == 'IT') is not None
    assert megan_row.find('td', string=lambda s: s and s.strip() == '3999') is not None
    assert megan_row.find('td', string=lambda s: s and s.strip() == 'megan_wolfgrill@abnor.com') is not None

def test_delete_employee(client, app):
    with app.app_context():
        emp = Employee.query.filter_by(id=1).first()
        assert emp is not None, "Employee with id=1 should exist before deletion"
        emp_name = f"{emp.fname} {emp.lname}"

    response = client.post('/delete_emp/1/', follow_redirects=True)
    
    # Verify successful processing and redirect
    assert response.status_code == 200
    assert f'{emp_name} deleted from database'.encode() in response.data

    # Check database to confirm deletion
    with app.app_context():
        deleted_emp = Employee.query.filter_by(id=1).first()
        assert deleted_emp is None, "Employee should be deleted from database"

    # Verify employee not on index page
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    maya_cell = soup.find('td', string=lambda s: s and s.strip() == 'Maya')
    assert maya_cell is None, "Deleted employee 'Maya' still appears in table"

def test_delete_nonexistent_employee(client):
    response = client.post('/delete_emp/99/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Database error' in response.data, "Should return flash error message"

def test_delete_employee_via_get_fails(client, app):
    # Make GET request instead of POST
    response = client.get('/delete_emp/1/', follow_redirects=True)
    
    # Employee should still exist
    with app.app_context():
        emp = Employee.query.filter_by(id=1).first()
        assert emp is not None
    
    assert response.status_code == 405
    assert b'Method Not Allowed' in response.data, "Should return generic 405 page"

def test_update_route_loads_correctly(client):
    response = client.get('/update_emp/1/')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser') 
    assert soup.title.string == 'Update - Contacts', "'update.html' page not loaded" 

def test_update_route_populates_employee(client):
    response = client.get('/update_emp/1/')
    soup = BeautifulSoup(response.data, 'html.parser')

    fname_input = soup.find('input', id='fname')
    assert fname_input is not None, "First name input not found"
    assert fname_input.get('value') == 'Maya', "First name value not populated correctly"
    
    lname_input = soup.find('input', id='lname')
    assert lname_input is not None, "Last name input not found"
    assert lname_input.get('value') == 'Name', "Last name value not populated correctly"
    
    dept_select = soup.find('select', id='dept')
    assert dept_select is not None, "Department select not found"
    
    selected_option = dept_select.find('option', selected=True)
    assert selected_option is not None, "No department option selected"
    assert selected_option.get('value') == 'IT', "Incorrect department selected"
    
    ext_input = soup.find('input', id='ext')
    assert ext_input is not None, "Extension input not found"
    assert ext_input.get('value') == '3234', "Extension value not populated correctly" 

def test_update_employee(client, app):
    # Verify the initial state of employee with id=1
    with app.app_context():
        # emp = Employee.query.get(1)
        emp = Employee.query.filter_by(id=1).first()
        assert emp.ext == '3234'  # Initial extension value

    update_data = {
        'fname': 'Maya',
        'lname': 'Name',
        'dept': 'IT',
        'ext': '3999'  # Updated extension
    }

    response = client.post('/update_emp/1/', data=update_data, follow_redirects=True)
    
    assert response.status_code == 200
    # Check flash message
    assert b'Maya Name updated in database' in response.data

    # Check database 
    with app.app_context():
        updated_emp = Employee.query.filter_by(id=1).first()
        assert updated_emp is not None
        assert updated_emp.ext == '3999'  
        assert updated_emp.email == 'maya_name@adnor.com'  

    # Verify employee appears index page
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    maya_cell = soup.find('td', string=lambda s: s and s.strip() == 'Maya')
    assert maya_cell is not None, "Employee 'Maya' not found in table"
    
    maya_row = maya_cell.find_parent('tr')
    
    assert maya_row.find('a', string=lambda s: s and s.strip() == 'Name') is not None
    assert maya_row.find('td', string=lambda s: s and s.strip() == 'IT') is not None
    assert maya_row.find('td', string=lambda s: s and s.strip() == '3999') is not None  # Updated extension
    assert maya_row.find('td', string=lambda s: s and s.strip() == 'maya_name@adnor.com') is not None

def test_update_nonexistent_employee(client):
    response = client.post('/update_emp/99/', follow_redirects=True)
    assert response.status_code == 404
    assert b'Not Found' in response.data, "Should return generic 404 page"
