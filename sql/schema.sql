CREATE DATABASE IF NOT EXISTS lab_inventory
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE lab_inventory;

CREATE TABLE IF NOT EXISTS lab (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_lab VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS komputer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_lab INT NOT NULL,
    kode_pc VARCHAR(50) NOT NULL UNIQUE,
    monitor ENUM('Baik', 'Perlu Perbaikan', 'Rusak') NOT NULL DEFAULT 'Baik',
    cpu ENUM('Baik', 'Perlu Perbaikan', 'Rusak') NOT NULL DEFAULT 'Baik',
    keyboard ENUM('Baik', 'Perlu Perbaikan', 'Rusak') NOT NULL DEFAULT 'Baik',
    mouse ENUM('Baik', 'Perlu Perbaikan', 'Rusak') NOT NULL DEFAULT 'Baik',
    kondisi ENUM('Baik', 'Perlu Perbaikan', 'Rusak') NOT NULL DEFAULT 'Baik',
    catatan TEXT,
    CONSTRAINT fk_komputer_lab FOREIGN KEY (id_lab)
        REFERENCES lab(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS item_lab (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_lab INT NOT NULL,
    kode_item VARCHAR(50) NOT NULL UNIQUE,
    nama_item VARCHAR(120) NOT NULL,
    kondisi ENUM('Baik', 'Perlu Perbaikan', 'Rusak') NOT NULL DEFAULT 'Baik',
    catatan TEXT,
    CONSTRAINT fk_item_lab FOREIGN KEY (id_lab)
        REFERENCES lab(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
