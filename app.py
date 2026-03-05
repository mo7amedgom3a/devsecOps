import os
import sqlite3
import subprocess
import pickle
import hashlib
from flask import Flask, request

app = Flask(__name__)

# ---------------------------------------------------------
# VULNERABILITY 1: Hardcoded Secrets & Tokens
# Secret scanners (like Snyk or TruffleHog) will flag these immediately.
# ---------------------------------------------------------
AWS_ACCESS_KEY_ID = "fakeAKIAIOSFODNN7EXAMPLE" 
AWS_SECRET_ACCESS_KEY = "fakefwJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD = "fake_super_secret_db_password_123!"
JWT_SECRET = "fake_my_jwt_secret_token"
GITHUB_PERSONAL_ACCESS_TOKEN = "fake_ghp_abc123def456ghi789jkl012mno345pqr678"

@app.route('/ping')
def ping():
    # ---------------------------------------------------------
    # VULNERABILITY 2: Command Injection (OS Command)
    # ---------------------------------------------------------
    target = request.args.get('ip', '127.0.0.1')
    # DANGEROUS: Passing unvalidated user input directly to a shell command.
    # An attacker could pass: 127.0.0.1; cat /etc/passwd
    output = subprocess.check_output(f"ping -c 1 {target}", shell=True)
    return output

@app.route('/user')
def get_user():
    # ---------------------------------------------------------
    # VULNERABILITY 3: SQL Injection (SQLi)
    # ---------------------------------------------------------
    username = request.args.get('username')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # DANGEROUS: Using string formatting for SQL queries instead of parameterized queries.
    # An attacker could pass: admin' OR '1'='1
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    user = cursor.fetchone()
    return str(user)

@app.route('/calculate')
def calculate():
    # ---------------------------------------------------------
    # VULNERABILITY 4: Arbitrary Code Execution
    # ---------------------------------------------------------
    expression = request.args.get('expr', '2 + 2')
    # DANGEROUS: eval() executes arbitrary Python code. 
    # An attacker could pass: __import__('os').system('rm -rf /')
    result = eval(expression)
    return str(result)

@app.route('/load')
def load_data():
    # ---------------------------------------------------------
    # VULNERABILITY 5: Insecure Deserialization
    # ---------------------------------------------------------
    data = request.args.get('data')
    if data:
        # DANGEROUS: The pickle module is not secure. Unpickling untrusted data 
        # can execute arbitrary code during the deserialization process.
        parsed_data = pickle.loads(bytes.fromhex(data))
        return str(parsed_data)
    return "No data provided"

@app.route('/register', methods=['POST'])
def register():
    # ---------------------------------------------------------
    # VULNERABILITY 6: Weak Cryptography
    # ---------------------------------------------------------
    password = request.form.get('password')
    if not password:
        return "Password required", 400
    # DANGEROUS: MD5 is cryptographically broken and highly vulnerable to collision 
    # and brute-force attacks. Passwords should use bcrypt or Argon2.
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    return f"User registered with hash: {hashed_password}"

if __name__ == '__main__':
    # ---------------------------------------------------------
    # VULNERABILITY 7: Misconfiguration
    # ---------------------------------------------------------
    # DANGEROUS: Running Flask in debug mode in a public-facing way exposes 
    # the interactive Werkzeug debugger, allowing remote code execution.
    app.run(host='0.0.0.0', port=8080, debug=True)