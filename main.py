from __future__ import annotations

from storage.mysql_storage import MySQLInventoryStorage
from ui.app import InventoryApp


def main() -> None:
    print("\n" + "=" * 54)
    print(" MINI SISTEM MANAJEMEN INVENTARIS LAB KOMPUTER")
    print("=" * 54)
    print("Database: MySQL")

    storage = None
    try:
        storage = MySQLInventoryStorage.from_environment()
        storage.initialize()
        print("Berhasil terhubung ke MySQL dan tabel siap digunakan.")
        InventoryApp(storage=storage).run()
    except Exception as exc:
        print(f"\nGagal menjalankan aplikasi dengan MySQL: {exc}")
        print("Pastikan MySQL aktif, database lab_inventory sudah dibuat, dan konfigurasi .env/variabel lingkungan benar.")
        raise SystemExit(1)
    finally:
        if storage is not None:
            storage.close()


if __name__ == "__main__":
    main()
