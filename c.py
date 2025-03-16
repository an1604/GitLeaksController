"""
This file contains intentional security vulnerabilities for testing Checkmarx SAST.
DO NOT USE THIS CODE IN PRODUCTION.
"""
import sqlite3
import subprocess
from flask import Flask, request, redirect

app = Flask(__name__)

# Vulnerability 1: Hardcoded credentials
API_KEY = "1234567890abcdef"
PASSWORD = "supersecretpassword123"
DB_CONNECTION = "mysql://admin:Password123@database.example.com/app_db"


# Vulnerability 2: SQL Injection
@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Vulnerable SQL query - no parameterization
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return str(user)


# Vulnerability 3: Command Injection
@app.route('/run_command')
def run_command():
    cmd = request.args.get('cmd')
    # Vulnerable command execution
    output = subprocess.check_output(cmd, shell=True)
    return output.decode()


# Vulnerability 4: Path Traversal
@app.route('/get_file')
def get_file():
    filename = request.args.get('filename')
    # Vulnerable path handling
    with open(filename, 'r') as f:
        content = f.read()
    return content


# Vulnerability 5: Insecure Redirect
@app.route('/redirect')
def redirect_url():
    url = request.args.get('url')
    # Vulnerable redirect
    return redirect(url)


if __name__ == '__main__':
    app.run(debug=True)  # Running in debug mode - another security issue
