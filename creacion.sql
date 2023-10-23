DROP DATABASE IF EXISTS foro;
CREATE DATABASE foro;

USE foro;

CREATE TABLE roles (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre_rol VARCHAR(50)
);

INSERT INTO roles (nombre_rol) VALUES ('usuario'), ('moderador'), ('admin');

CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(25) not null,
  email VARCHAR(100) not null,
  contrasena VARCHAR(256) not null,
  id_rol INT not null,
  FOREIGN KEY (id_rol) REFERENCES roles(id_rol) on DELETE CASCADE on UPDATE CASCADE,
  CONSTRAINT usuarios_uk1 UNIQUE (usuario,email)
);

CREATE TABLE temas (
  id_tema INT AUTO_INCREMENT PRIMARY KEY,
  tema VARCHAR(50) not null
);

CREATE TABLE posts (
  id_post INT AUTO_INCREMENT PRIMARY KEY,
  fecha DATE,
  titulo VARCHAR(100) not null,
  contenido VARCHAR(2500) not null,
  ruta VARCHAR(200) not null,
  id_usuario INT,
  id_tema INT,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) on DELETE CASCADE on UPDATE CASCADE,
  FOREIGN KEY (id_tema) REFERENCES temas(id_tema) on DELETE CASCADE on UPDATE CASCADE
);

CREATE TABLE respuestas (
  id_post INT,
  id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT,
  contenido VARCHAR(2500) not null,
  ruta VARCHAR(200) not null,
  fecha DATE,
  FOREIGN KEY (id_post) REFERENCES posts(id_post) on DELETE CASCADE on UPDATE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) on DELETE CASCADE on UPDATE CASCADE
);

INSERT INTO temas (tema) VALUES ('Motos'), ('Rutas'), ('Averías');

DROP USER IF EXISTS 'foroUser'@'localhost';

CREATE USER 'foroUser'@'localhost' IDENTIFIED BY 'f0r0DB';

REVOKE ALL PRIVILEGES ON *.* FROM 'foroUser'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE ON foro.* TO 'foroUser'@'localhost';