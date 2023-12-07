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

# Landing page (login page)
@app.route('/')
def login():
    # Clear any previous login error
    session.pop('error', None)
    return render_template('login.html', error=session.get('error'))

# Login route
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Since this is a personal cloud database app, there is only one username and
    # password that will login to the database. This is a simple method to log in
    if username == config['database']['user'] and password == config['database']['password']:
        session['logged_in'] = True
        return redirect(url_for('index'))
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
    
    if search_query:
        sql = "SELECT * FROM employees WHERE CONCAT(emp_no, birth_date, first_name, last_name, gender, hire_date) LIKE %s LIMIT %s OFFSET %s"
        cursor.execute(sql, ('%' + search_query + '%', per_page, offset))
    else:
        sql = "SELECT * FROM employees LIMIT %s OFFSET %s"
        cursor.execute(sql, (per_page, offset))

    data = cursor.fetchall()

    # Count total records for pagination
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_records = cursor.fetchone()[0]
    max_pages = (total_records // per_page) + (total_records % per_page > 0)

    pagination = max_pages > 1

    return render_template('index.html', data=data, page=page, max_pages=max_pages, pagination=pagination, search=search_query)

if __name__ == '__main__':
    app.run()
