from flask import Flask, render_template, request
import mysql.connector
import configparser

app = Flask(__name__)

# MySQL configuration
config = configparser.ConfigParser()
config.read('config.ini')

db = mysql.connector.connect(
    host = config['database']['host'],
    user = config['database']['user'],
    password = config['database']['password'],
    database = config['database']['database']
)

@app.route('/')
def index():
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
    app.run(debug=True)
