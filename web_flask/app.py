from flask import Flask, request, render_template, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Asegúrate de definir una clave secreta para las sesiones

# Función para obtener la conexión de la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="grupo_bbdd"
    )

# Ruta de inicio para mostrar los juegos
@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()  # Obtener todos los juegos de la base de datos
    db.close()
    
    # Pasamos los juegos al template
    return render_template('inicio.html', games=games)

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 

        db = get_db_connection()
        cursor = db.cursor()

        # Insertar usuario en la base de datos (SIN cifrado)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        db.close()

        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        db.close()

        if not user:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('login'))

        stored_password = user['password']

        # Comparar contraseñas en texto plano (OJO: INSEGURO)
        if password == stored_password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Bienvenido, {user["username"]}!', 'success')
            return redirect(url_for('index'))  # Redirigir a la página principal
        else:
            flash('Contraseña incorrecta', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Eliminar toda la sesión
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))  # Redirigir al inicio

# Ruta para mostrar juegos
@app.route('/games')
def games():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM games")  # Consulta para obtener todos los juegos
    games = cursor.fetchall()  # Obtener todos los juegos de la base de datos
    db.close()

    return render_template('games.html', games=games)  # Pasamos la lista de juegos al template

# Ruta para mostrar reseñas de juegos
@app.route('/games/reviews')
def reviews():
    if request.method == 'POST':
        content = request.form['content']

        db = get_db_connection()
        cursor = db.cursor()

        # Insertar usuario en la base de datos (SIN cifrado)
        cursor.execute("INSERT INTO reviews (username) VALUES (%s)", (content))
        db.commit()
        db.close()

        flash('Review añadida correctamente', 'success')
        ## return redirect(url_for('reviews'))
    return render_template('reviews.html')

def filter_category(category):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM games WHERE category = %s", (category,))
    games = cursor.fetchall()  # Obtener todos los juegos de la base de datos
    db.close()
    return render_template('games.html', games=games)  # Pasamos la lista de juegos al template

if __name__ == '__main__':
    app.run(debug=True)
    
