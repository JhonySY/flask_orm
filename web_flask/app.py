from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Asegúrate de definir una clave secreta para las sesiones

# Función para obtener la conexión de la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="grupo_bbdd"
    )

# Ruta de inicio para mostrar los juegos
@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()

    # Obtener todos los juegos
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()  # Obtener todos los juegos de la base de datos

    # Obtener todas las categorías únicas
    cursor.execute("SELECT DISTINCT category FROM games")
    categories = cursor.fetchall()  # Obtener todas las categorías

    db.close()

    # Pasamos los juegos y las categorías al template
    return render_template('inicio.html', games=games, categories=categories)


# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # OJO: Guardando sin cifrar 😨

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

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Eliminar toda la sesión
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))  # Redirigir al inicio

# Ruta del perfil del usuario
@app.route('/profile')
def profile():
    # Verificar si el usuario está autenticado
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu perfil.', 'danger')
        return redirect(url_for('login'))  # Redirige a la página de login si no está autenticado

    user_id = session['user_id']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Obtener información del usuario desde la base de datos usando el user_id
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()  # Obtener los datos del usuario

    db.close()

    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('index'))  # Si no se encuentra el usuario, redirige al inicio
    
    return render_template('profile.html', user=user)  # Pasamos los datos del usuario al template


# Ruta para mostrar juegos
@app.route('/games', methods=['GET'])
def games():
    category = request.args.get('category')  # Obtener el parámetro de categoría desde la URL
    db = get_db_connection()
    cursor = db.cursor()

    if category:
        # Si se especifica una categoría, filtramos los juegos por categoría
        cursor.execute("SELECT * FROM games WHERE category = %s", (category,))
    else:
        # Si no se especifica categoría, mostramos todos los juegos
        cursor.execute("SELECT * FROM games")
    
    games = cursor.fetchall()  # Obtener los juegos de la base de datos
    db.close()

    return render_template('games.html', games=games, category=category)  # Pasamos los juegos y la categoría al template

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

# Ruta para mostrar reseñas de un juego específico
@app.route('/game_reviews/<int:game_id>', methods=['GET', 'POST'])
def game_reviews(game_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Obtener el juego por su ID
    cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
    game = cursor.fetchone()
    
    # Verificar si el juego existe
    if not game:
        flash('Juego no encontrado', 'danger')
        return redirect(url_for('index'))

    # Obtener todas las reseñas junto con el nombre de usuario
    cursor.execute("""
        SELECT reviews.content, users.username 
        FROM reviews 
        JOIN users ON reviews.user_id = users.id
        WHERE reviews.game_id = %s
    """, (game_id,))
    reviews = cursor.fetchall()

    if request.method == 'POST':
        # Verificar si el usuario ha iniciado sesión antes de publicar una reseña
        if 'user_id' not in session:
            flash('Debes iniciar sesión para publicar una reseña.', 'danger')
            return redirect(url_for('login'))  # Redirigir a la página de login
        
        content = request.form['content']
        user_id = session['user_id']  # Obtener el ID del usuario desde la sesión

        # Insertar la nueva reseña
        cursor.execute(
            "INSERT INTO reviews (game_id, content, user_id) VALUES (%s, %s, %s)",
            (game_id, content, user_id)
        )
        db.commit()
        flash('Reseña añadida correctamente', 'success')
        return redirect(url_for('game_reviews', game_id=game_id))  # Redirigir a la misma página

    db.close()
    return render_template('reviews.html', game=game, reviews=reviews)


def username_from_review(review):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users WHERE id = %s", (review[1],))
    username = cursor.fetchone()
    db.close()
    return username[0]

@app.route('/toggle_like/<int:game_id>', methods=['POST'])
def toggle_like(game_id):
    if 'user_id' not in session:
        return jsonify({"error": "No autenticado"}), 401  # No autorizado

    user_id = session['user_id']
    db = get_db_connection()
    cursor = db.cursor()

    # Verificar si el usuario ya ha dado like a este juego
    cursor.execute("SELECT * FROM game_likes WHERE user_id = %s AND game_id = %s", (user_id, game_id))
    like = cursor.fetchone()

    if like:
        # Si el usuario ya dio like, eliminarlo y restar 1 al contador
        cursor.execute("DELETE FROM game_likes WHERE user_id = %s AND game_id = %s", (user_id, game_id))
        cursor.execute("UPDATE games SET like_count = like_count - 1 WHERE id = %s AND like_count > 0", (game_id,))
        liked = False
    else:
        # Si no, agregar el like y sumar 1 al contador
        cursor.execute("INSERT INTO game_likes (user_id, game_id) VALUES (%s, %s)", (user_id, game_id))
        cursor.execute("UPDATE games SET like_count = like_count + 1 WHERE id = %s", (game_id,))
        liked = True

    # Obtener la nueva cantidad de likes después de la actualización
    cursor.execute("SELECT like_count FROM games WHERE id = %s", (game_id,))
    like_count = cursor.fetchone()[0]

    db.commit()
    db.close()

    return jsonify({"liked": liked, "like_count": like_count})



if __name__ == '__main__':
    app.run(debug=True)

