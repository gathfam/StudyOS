import sqlite3

def initializeDatabase():
    """Membuat tabel berdasarkan skema minimalis StudyOS jika belum ada."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            description TEXT,
            due_date TEXT,
            planned_date TEXT,
            priority TEXT CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH')) DEFAULT 'MEDIUM',
            completed INTEGER CHECK(completed IN (0, 1)) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            deadline_date TEXT NOT NULL,
            urgency_level TEXT CHECK(urgency_level IN ('LOW', 'MEDIUM', 'HIGH')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            note_type TEXT DEFAULT 'QUICK',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type TEXT CHECK(session_type IN ('POMODORO', 'SHORT_BREAK', 'LONG_BREAK')),
            duration INTEGER NOT NULL,
            completed INTEGER CHECK(completed IN (0, 1)) DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS progress_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            completed_tasks INTEGER DEFAULT 0,
            focus_sessions INTEGER DEFAULT 0,
            weekly_progress REAL DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    # Import get_connection secara lokal untuk menghindari circular import
    try:
        from .connection import getConnection
    except ImportError:
        from connection import getConnection
    conn = getConnection()

    try:
        cursor = conn.cursor()
        for query in queries:
            cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

