from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'csc312_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'miva_flask_db'
}


def connect_db():
    return mysql.connector.connect(**db_config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('signup.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM tbl_user WHERE username = %s', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Username already taken.', 'warning')
                return render_template('signup.html')

            cursor.execute(
                'INSERT INTO tbl_user (username, password) VALUES (%s, %s)',
                (username, hashed_password)
            )
            conn.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('signup'))

        except Error as e:
            flash(f'Database error: {e}', 'danger')
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)