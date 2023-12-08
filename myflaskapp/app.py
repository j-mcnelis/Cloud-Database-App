from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import configparser

app = Flask(__name__)

# MySQL configuration
config = configparser.ConfigParser()
config.read('config.ini')
app.secret_key = config['database']['secret_key']

db = mysql.connector.connect(
    host = config['database']['host'],
    user = config['database']['user'],
    password = config['database']['password'],
    database = config['database']['database']
)

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
    if username == config['database']['user'] and password == config['database']['password']:
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
        # Define the columns based on the selected filter
        columns = ['emp_no', 'birth_date', 'first_name', 'last_name', 'gender', 'hire_date']

        # Build the WHERE clause based on the selected filter
        if filter_by != 'all':
            where_clause = f"LOWER({filter_by}) LIKE %s"
        else:
            where_clause = ' OR '.join([f"LOWER({col}) LIKE %s" for col in columns])

        sql = f"SELECT * FROM employees WHERE {where_clause}"

        # Execute the query with the search query and selected filter
        cursor.execute(sql, (['%' + search_query.lower() + '%'] if filter_by != 'all' else ['%' + search_query.lower() + '%'] * len(columns)))

        data = cursor.fetchall()

        total_records = len(data)
        total_pages = 1 if total_records == 0 else (total_records // per_page) + (total_records % per_page > 0)

        # Paginate the results for display
        data = data[offset:offset + per_page]
    else:
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // per_page) + (total_records % per_page > 0)

        sql = "SELECT * FROM employees LIMIT %s OFFSET %s"
        cursor.execute(sql, (per_page, offset))
        data = cursor.fetchall()

    return render_template('index.html', data=data, page=page, total_pages=total_pages, search=search_query, filter=filter_by)

if __name__ == '__main__':
    app.run()
