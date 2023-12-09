from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc
import os

app = Flask(__name__)

server = os.environ.get('DB_SERVER')
database = os.environ.get('DB_DBASE')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
driver = os.environ.get('DB_DRIVER')
app.secret_key = os.environ.get('DB_SKEY')

connection_string =f'DRIVER={driver};SERVER={server};DATABASE={database};UID={db_user};Pwd={db_password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
db = pyodbc.connect(connection_string)

# Login page
@app.route('/')
def defaultLog():
    return render_template('login.html')

# Login page
@app.route('/login')
def login():
    # Clear any previous login error
    session.pop('error', None)
    return render_template('login.html', error=session.get('error'))

# Before each request, check if the user is logged in
@app.before_request
def check_login():
    if not session.get('logged_in') and not request.path.startswith('/login'):
        return redirect(url_for('login'))

# Landing page (home page)
@app.route('/home')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Since this is a personal cloud database app, there is only one username and
    # password that will login to the database. This is a simple method to log in
    if username == db_user and password == db_password:
        session['logged_in'] = True
        return redirect(url_for('home'))
    else:
        flash('Incorrect Username/Password', 'error')
        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    # Check for user log in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    cursor = db.cursor()

    search_query = request.args.get('search', '')
    filter_by = request.args.get('filter', 'all')  # Default to searching in all columns

    if search_query:
    # Replace 'employees' with your Azure SQL table name
        columns = ['emp_no', 'birth_date', 'first_name', 'last_name', 'gender', 'hire_date']
        # Adjust the WHERE clause based on Azure SQL syntax
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE ?"
        else:
            # Use OR to combine all columns for the "All Columns" filter
            where_clause = ' OR '.join([f"LOWER({col}) LIKE ?" for col in columns])
        
        sql = f"SELECT * FROM employees.employees WHERE {where_clause}"
    
        # Use ? as a placeholder for parameters in Azure SQL queries
        if filter_by != 'all':
            cursor.execute(sql, ['%' + search_query.lower() + '%'])
        else:
            # Repeat the search_query parameter for each column in the "All Columns" filter
            cursor.execute(sql, (['%' + search_query.lower() + '%'] * len(columns)))
            
        data = cursor.fetchall()

        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        # Paginate the results for display
        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees.employees")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        # Replace 'employees' with your Azure SQL table name
        sql = "SELECT * FROM employees.employees ORDER BY emp_no OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        cursor.execute(sql, (offset, per_page))
        data = cursor.fetchall()

    return render_template('index.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

# Salaries route
@app.route('/salaries')
def salaries():
    # Check for user log in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    cursor = db.cursor()

    search_query = request.args.get('search', '')
    filter_by = request.args.get('filter', 'all')  # Default to searching in all columns

    if search_query:
        columns = ['emp_no', 'salary', 'from_date', 'to_date']
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE ?"
        else:
            where_clause = ' OR '.join([f"LOWER({col}) LIKE ?" for col in columns])

        sql = f"SELECT * FROM employees.salaries WHERE {where_clause}"

        if filter_by != 'all':
            cursor.execute(sql, ['%' + search_query.lower() + '%'])
        else:
            cursor.execute(sql, (['%' + search_query.lower() + '%'] * len(columns)))

        data = cursor.fetchall()
        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees.salaries")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        sql = "SELECT * FROM employees.salaries ORDER BY emp_no OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        cursor.execute(sql, (offset, per_page))
        data = cursor.fetchall()

    return render_template('salaries.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

# Titles route
@app.route('/titles')
def titles():
    # Check for user log in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    cursor = db.cursor()

    search_query = request.args.get('search', '')
    filter_by = request.args.get('filter', 'all')  # Default to searching in all columns

    if search_query:
        columns = ['emp_no', 'title', 'from_date', 'to_date']
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE ?"
        else:
            where_clause = ' OR '.join([f"LOWER({col}) LIKE ?" for col in columns])

        sql = f"SELECT * FROM employees.titles WHERE {where_clause}"

        if filter_by != 'all':
            cursor.execute(sql, ['%' + search_query.lower() + '%'])
        else:
            cursor.execute(sql, (['%' + search_query.lower() + '%'] * len(columns)))

        data = cursor.fetchall()
        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees.titles")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        sql = "SELECT * FROM employees.titles ORDER BY emp_no OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        cursor.execute(sql, (offset, per_page))
        data = cursor.fetchall()

    return render_template('titles.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

# dept_emp route
@app.route('/dept_emp')
def dept_emp():
    # Check for user log in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    cursor = db.cursor()

    search_query = request.args.get('search', '')
    filter_by = request.args.get('filter', 'all')  # Default to searching in all columns

    if search_query:
        columns = ['emp_no', 'dept_no', 'from_date', 'to_date']
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE ?"
        else:
            where_clause = ' OR '.join([f"LOWER({col}) LIKE ?" for col in columns])

        sql = f"SELECT * FROM employees.dept_emp WHERE {where_clause}"

        if filter_by != 'all':
            cursor.execute(sql, ['%' + search_query.lower() + '%'])
        else:
            cursor.execute(sql, (['%' + search_query.lower() + '%'] * len(columns)))

        data = cursor.fetchall()
        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees.dept_emp")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        sql = "SELECT * FROM employees.dept_emp ORDER BY emp_no OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        cursor.execute(sql, (offset, per_page))
        data = cursor.fetchall()

    return render_template('dept_emp.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

# dept_manager route
@app.route('/dept_manager')
def dept_manager():
    # Check for user log in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    cursor = db.cursor()

    search_query = request.args.get('search', '')
    filter_by = request.args.get('filter', 'all')  # Default to searching in all columns

    if search_query:
        columns = ['emp_no', 'dept_no', 'from_date', 'to_date']
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE ?"
        else:
            where_clause = ' OR '.join([f"LOWER({col}) LIKE ?" for col in columns])

        sql = f"SELECT * FROM employees.dept_manager WHERE {where_clause}"

        if filter_by != 'all':
            cursor.execute(sql, ['%' + search_query.lower() + '%'])
        else:
            cursor.execute(sql, (['%' + search_query.lower() + '%'] * len(columns)))

        data = cursor.fetchall()
        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees.dept_manager")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        sql = "SELECT * FROM employees.dept_manager ORDER BY emp_no OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        cursor.execute(sql, (offset, per_page))
        data = cursor.fetchall()

    return render_template('dept_manager.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

# departments route
@app.route('/departments')
def departments():
    # Check for user log in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    cursor = db.cursor()

    search_query = request.args.get('search', '')
    filter_by = request.args.get('filter', 'all')  # Default to searching in all columns

    if search_query:
        columns = ['dept_no', 'dept_name']
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE ?"
        else:
            where_clause = ' OR '.join([f"LOWER({col}) LIKE ?" for col in columns])

        sql = f"SELECT * FROM employees.departments WHERE {where_clause}"

        if filter_by != 'all':
            cursor.execute(sql, ['%' + search_query.lower() + '%'])
        else:
            cursor.execute(sql, (['%' + search_query.lower() + '%'] * len(columns)))

        data = cursor.fetchall()
        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees.departments")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        sql = "SELECT * FROM employees.departments ORDER BY dept_no OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        cursor.execute(sql, (offset, per_page))
        data = cursor.fetchall()

    return render_template('departments.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

if __name__ == '__main__':
    app.run()
