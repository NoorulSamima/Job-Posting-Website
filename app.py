from flask import Flask, render_template, request
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        port=int(os.environ.get('DB_PORT', 3306))
    )

@app.route('/', methods=['GET'])
def index():
    title = request.args.get('title', '').strip()
    location = request.args.get('location', '').strip()
    job_type = request.args.get('job_type', '').strip()
    slider_value = request.args.get('salary', type=int)

    salary_in_rs = slider_value * 100000 if slider_value else None

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if title:
        query += " AND LOWER(job_title) LIKE %s"
        params.append(f"%{title.lower()}%")

    if location:
        query += " AND LOWER(location) LIKE %s"
        params.append(f"%{location.lower()}%")

    if job_type:
        query += " AND job_type = %s"
        params.append(job_type)

    if salary_in_rs:
        query += " AND %s BETWEEN salary_min AND salary_max"
        params.append(salary_in_rs)

    query += " ORDER BY id DESC"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", jobs=jobs, slider_value=slider_value)


@app.route('/submit', methods=['POST'])
def submit():
    job_title = request.form['job_title']
    company_name = request.form['company_name']
    location = request.form['location']
    job_type = request.form['job_type']
    salary_min = request.form['salary_min']
    salary_max = request.form['salary_max']
    description = request.form['description']
    deadline = request.form['deadline']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (job_title, company_name, location, job_type, salary_min, salary_max, description, deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (job_title, company_name, location, job_type, salary_min, salary_max, description, deadline))
    conn.commit()
    cursor.close()
    conn.close()

    return """
        <script>
        alert('Job Posted successfully');
        window.location.href = "/";
        </script>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)  # Render requires public binding
