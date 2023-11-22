# app.py
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Konfigurasi koneksi database
db_config = {
    'host': 'sql-srv.mysql.database.azure.com',
    'user': 'adminkelompok10',
    'password': '4dm1nKelompok10',
    'database': 'db_kelompok10', 
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # Mengambil data dari database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM portfolio")
    portfolios = cursor.fetchall()
    connection.close()

    return render_template('index.html', portfolios=portfolios)

@app.route('/add', methods=['POST'])
def add_portfolio():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        university = request.form['university']
        major = request.form['major']
        skills = request.form['skills']

        # Periksa apakah file ada dalam request
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # Periksa apakah file memiliki nama dan ekstensi yang diizinkan
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        # Simpan file di direktori uploads
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Menyimpan data ke database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO portfolio (name, description, university, major, skills, profile_image) VALUES (%s, %s, %s, %s, %s, %s)", (name, description, university, major, skills, filename))
        connection.commit()
        connection.close()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_portfolio(id):
    # Menghapus data dari database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM portfolio WHERE id = %s", (id,))
    connection.commit()
    connection.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
