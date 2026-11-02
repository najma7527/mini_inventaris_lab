import os
import mysql.connector
from mysql.connector import Error
from storage.base import InventoryStorage


class MySQLInventoryStorage(InventoryStorage):
    def __init__(self, host, port, user, password, database):
        self.config = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database,
            "autocommit": True,
        }
        self.connection = mysql.connector.connect(**self.config)

    @classmethod
    def from_environment(cls):
        # Environment variables are optional; sensible local defaults are provided.
        return cls(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=os.getenv("MYSQL_PORT", "3306"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "lab_inventory"),
        )

    def initialize(self):
        cursor = self.connection.cursor()
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.close()

    @staticmethod
    def _row_to_dict(row):
        return {
            "id": row[0], "code": row[1], "name": row[2],
            "category": row[3], "quantity": row[4],
            "condition": row[5], "location": row[6],
            "notes": row[7] or "", "updated_at": row[8] or "",
        }

    def list_items(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, code, name, category, quantity, item_condition,
                   location, notes, updated_at
            FROM inventory_items ORDER BY id
        """)
        result = [self._row_to_dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def add_item(self, item):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO inventory_items
                (code, name, category, quantity, item_condition, location, notes, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item["code"], item["name"], item["category"], item["quantity"],
                item["condition"], item["location"], item.get("notes", ""),
                item["updated_at"]
            ))
            item_id = cursor.lastrowid
            cursor.close()
            saved = dict(item)
            saved["id"] = item_id
            return saved
        except Error:
            cursor.close()
            raise

    def update_item(self, item_id, item):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE inventory_items SET code=%s, name=%s, category=%s,
                quantity=%s, item_condition=%s, location=%s, notes=%s, updated_at=%s
                WHERE id=%s
            """, (
                item["code"], item["name"], item["category"], item["quantity"],
                item["condition"], item["location"], item.get("notes", ""),
                item["updated_at"], item_id
            ))
            changed = cursor.rowcount > 0
            cursor.close()
            return changed
        except Error:
            cursor.close()
            raise

    def delete_item(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM inventory_items WHERE id=%s", (item_id,))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
