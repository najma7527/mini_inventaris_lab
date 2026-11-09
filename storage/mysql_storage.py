import os
import mysql.connector
from mysql.connector import Error
<<<<<<< HEAD
=======
from storage.base import InventoryStorage
>>>>>>> c099629f0a35ab142effad5544cc14a4f5af6ca4


CONDITION_ENUM = "ENUM('Baik','Perlu Perbaikan','Rusak')"


<<<<<<< HEAD
class MySQLInventoryStorage():
=======
class MySQLInventoryStorage(InventoryStorage):
>>>>>>> c099629f0a35ab142effad5544cc14a4f5af6ca4
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
            CREATE TABLE IF NOT EXISTS lab (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama_lab VARCHAR(120) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS komputer (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_lab INT NOT NULL,
                kode_pc VARCHAR(50) NOT NULL UNIQUE,
                monitor {CONDITION_ENUM} NOT NULL DEFAULT 'Baik',
                cpu {CONDITION_ENUM} NOT NULL DEFAULT 'Baik',
                keyboard {CONDITION_ENUM} NOT NULL DEFAULT 'Baik',
                mouse {CONDITION_ENUM} NOT NULL DEFAULT 'Baik',
                kondisi {CONDITION_ENUM} NOT NULL DEFAULT 'Baik',
                catatan TEXT,
                CONSTRAINT fk_komputer_lab FOREIGN KEY (id_lab)
                    REFERENCES lab(id) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS item_lab (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_lab INT NOT NULL,
                kode_item VARCHAR(50) NOT NULL UNIQUE,
                nama_item VARCHAR(120) NOT NULL,
                kondisi {CONDITION_ENUM} NOT NULL DEFAULT 'Baik',
                catatan TEXT,
                CONSTRAINT fk_item_lab FOREIGN KEY (id_lab)
                    REFERENCES lab(id) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.close()

    def list_labs(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT l.id, l.nama_lab,
                   (SELECT COUNT(*) FROM komputer k WHERE k.id_lab = l.id),
                   (SELECT COUNT(*) FROM item_lab i WHERE i.id_lab = l.id)
            FROM lab l ORDER BY l.nama_lab
        """)
        rows = cursor.fetchall()
        cursor.close()
        return [{"id": row[0], "nama_lab": row[1], "jumlah_komputer": row[2], "jumlah_item": row[3]} for row in rows]

    def add_lab(self, lab):
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT INTO lab (nama_lab) VALUES (%s)", (lab["nama_lab"],))
            saved = {"id": cursor.lastrowid, "nama_lab": lab["nama_lab"]}
            cursor.close()
            return saved
        except Error:
            cursor.close()
            raise

    def update_lab(self, lab_id, lab):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE lab SET nama_lab=%s WHERE id=%s", (lab["nama_lab"], lab_id))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def delete_lab(self, lab_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM lab WHERE id=%s", (lab_id,))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def list_computers(self, lab_id=None):
        cursor = self.connection.cursor()
        query = """
            SELECT k.id, k.id_lab, l.nama_lab, k.kode_pc, k.monitor, k.cpu,
                   k.keyboard, k.mouse, k.kondisi, k.catatan
            FROM komputer k JOIN lab l ON l.id = k.id_lab
        """
        params = ()
        if lab_id is not None:
            query += " WHERE k.id_lab=%s"
            params = (lab_id,)
        query += " ORDER BY l.nama_lab, k.kode_pc"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [{"id": r[0], "id_lab": r[1], "nama_lab": r[2], "kode_pc": r[3],
                 "monitor": r[4], "cpu": r[5], "keyboard": r[6], "mouse": r[7],
                 "kondisi": r[8], "catatan": r[9] or ""} for r in rows]

    def add_computer(self, computer):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO komputer (id_lab, kode_pc, monitor, cpu, keyboard, mouse, kondisi, catatan)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, tuple(computer[key] for key in ("id_lab", "kode_pc", "monitor", "cpu", "keyboard", "mouse", "kondisi", "catatan")))
            saved = dict(computer)
            saved["id"] = cursor.lastrowid
            cursor.close()
            return saved
        except Error:
            cursor.close()
            raise

    def update_computer(self, computer_id, computer):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE komputer SET id_lab=%s, kode_pc=%s, monitor=%s, cpu=%s,
            keyboard=%s, mouse=%s, kondisi=%s, catatan=%s WHERE id=%s
        """, (computer["id_lab"], computer["kode_pc"], computer["monitor"], computer["cpu"],
              computer["keyboard"], computer["mouse"], computer["kondisi"], computer["catatan"], computer_id))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def delete_computer(self, computer_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM komputer WHERE id=%s", (computer_id,))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def list_lab_items(self, lab_id=None):
        cursor = self.connection.cursor()
        query = """
            SELECT i.id, i.id_lab, l.nama_lab, i.kode_item, i.nama_item, i.kondisi, i.catatan
            FROM item_lab i JOIN lab l ON l.id = i.id_lab
        """
        params = ()
        if lab_id is not None:
            query += " WHERE i.id_lab=%s"
            params = (lab_id,)
        query += " ORDER BY l.nama_lab, i.kode_item"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [{"id": r[0], "id_lab": r[1], "nama_lab": r[2], "kode_item": r[3],
                 "nama_item": r[4], "kondisi": r[5], "catatan": r[6] or ""} for r in rows]

    def add_lab_item(self, item):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO item_lab (id_lab, kode_item, nama_item, kondisi, catatan)
                VALUES (%s,%s,%s,%s,%s)
            """, (item["id_lab"], item["kode_item"], item["nama_item"], item["kondisi"], item["catatan"]))
            saved = dict(item)
            saved["id"] = cursor.lastrowid
            cursor.close()
            return saved
        except Error:
            cursor.close()
            raise

    def update_lab_item(self, item_id, item):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE item_lab SET id_lab=%s, kode_item=%s, nama_item=%s, kondisi=%s, catatan=%s
            WHERE id=%s
        """, (item["id_lab"], item["kode_item"], item["nama_item"], item["kondisi"], item["catatan"], item_id))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def delete_lab_item(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM item_lab WHERE id=%s", (item_id,))
        changed = cursor.rowcount > 0
        cursor.close()
        return changed

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
