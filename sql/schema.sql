-- Jalankan seluruh file ini di MySQL Workbench atau phpMyAdmin (tab SQL).
CREATE DATABASE IF NOT EXISTS lab_inventory
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lab_inventory;

CREATE TABLE IF NOT EXISTS inventory_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(80) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    item_condition VARCHAR(40) NOT NULL,
    location VARCHAR(120) NOT NULL,
    notes TEXT,
    updated_at VARCHAR(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contoh data awal. INSERT IGNORE mencegah kode barang duplikat jika file dijalankan lagi.
INSERT IGNORE INTO inventory_items
(code, name, category, quantity, item_condition, location, notes, updated_at)
VALUES
('PC-001', 'Komputer PC', 'Komputer', 20, 'Baik', 'Lab Komputer 1', 'Komputer untuk praktikum', NOW()),
('KEY-001', 'Keyboard USB', 'Periferal', 25, 'Baik', 'Lab Komputer 1', 'Keyboard standar', NOW()),
('MOU-001', 'Mouse USB', 'Periferal', 5, 'Rusak', 'Lab Komputer 2', 'Beberapa mouse perlu diperiksa', NOW());
