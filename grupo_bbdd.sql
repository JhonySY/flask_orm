DROP SCHEMA grupo_bbdd;
CREATE SCHEMA grupo_bbdd;
USE grupo_bbdd;

-- Crear tabla de usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Crear tabla de juegos
CREATE TABLE games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    like_count INT DEFAULT 0
);

-- Crear tabla de reseñas
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

SELECT g.name AS game_name, r.content AS review_content, u.username AS reviewer_name
FROM games g
JOIN reviews r ON g.id = r.game_id
JOIN users u ON r.user_id = u.id
WHERE g.id = 1;


INSERT INTO games (name, image, category, like_count)
VALUES
    ('The Witcher 3: Wild Hunt', 'https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg', 'RPG', 10),
    ('Minecraft', 'https://img.itch.zone/aW1hZ2UyL2phbS8zMjE3MzQvODg0Mzg1MS5wbmc=/original/m0k8TF.png', 'Sandbox', 5),
    ('Elden Ring', 'RPG', 'https://storage.googleapis.com/pod_public/750/216712.jpg', 50),
    ('The Legend of Zelda: Breath of the Wild', 'https://th.bing.com/th/id/R.0bfe1eb6d429147ba27211e31c327cc2?rik=guayMb5sTSfc%2fw&pid=ImgRaw&r=0', 'Adventure', 15);

INSERT INTO users (username, password)
VALUES
    ('jordi', '123'),
    ('jhony', '123');

INSERT INTO reviews (content, user_id, game_id)
VALUES
    ('Increíble juego, una experiencia épica, sin duda mi favorito.', 1, 1),
    ('Me encanta este juego, tiene una gran comunidad y creatividad.', 2, 2);