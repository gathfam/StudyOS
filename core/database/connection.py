import os
import sqlite3
from contextlib import contextmanager

dbName = "studyos.db"
dbPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", dbName))

def getConnection():
    """Mengembalikan koneksi SQLite yang terhubung ke database StudyOS."""
    parentDir = os.path.dirname(dbPath)
    if parentDir and not os.path.exists(parentDir):
        os.makedirs(parentDir, exist_ok=True)
        
    conn = sqlite3.connect(dbPath)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

class DatabaseManager:
    def __init__(self):
        self._initDb()

    def _getConnection(self):
        return getConnection()

    @contextmanager
    def session(self):
        """Context manager untuk handle transaksi SQL secara aman."""
        conn = self._getConnection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _initDb(self):
        """Membuat tabel berdasarkan skema minimalis StudyOS jika belum ada."""
        try:
            from .schema import initializeDatabase
        except ImportError:
            from schema import initializeDatabase
        initializeDatabase()



db = DatabaseManager()

if __name__ == "__main__":
    print("Testing SQLite connection...")
    print(f"Database Name: {dbName}")
    print(f"Database Path: {dbPath}")
    
    try:
        conn = getConnection()
        print("Successfully connected to the database!")
        
        # Ambil daftar semua tabel untuk verifikasi auto-create
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")
        
        conn.close()
        print("Database connection test passed successfully!")
    except Exception as e:
        print(f"Error testing database connection: {e}")
        exit(1)

