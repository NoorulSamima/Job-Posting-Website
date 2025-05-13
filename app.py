from flask import Flask, render_template, request
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", jobs=jobs)

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
