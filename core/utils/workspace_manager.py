import os
import shutil
import zipfile
import json
import sqlite3
from core.database import dbPath, getConnection

def getSettingsFilePath():
    """Mengembalikan path untuk settings.json."""
    # Simpan settings.json di direktori yang sama dengan database agar mudah dipindah
    return os.path.join(os.path.dirname(dbPath), "settings.json")

def exportWorkspace(targetZipPath):
    """Mengekspor seluruh workspace ke format zip (.studyos atau .zip)."""
    settingsPath = getSettingsFilePath()
    tempDir = os.path.join(os.path.dirname(dbPath), "temp_export")
    
    try:
        if os.path.exists(tempDir):
            shutil.rmtree(tempDir)
        os.makedirs(tempDir, exist_ok=True)
        
        # 1. Salin SQLite database
        shutil.copy2(dbPath, os.path.join(tempDir, "studyos.db"))
        
        # 2. Salin settings.json (jika ada)
        if os.path.exists(settingsPath):
            shutil.copy2(settingsPath, os.path.join(tempDir, "settings.json"))
        else:
            # Jika belum ada, buat file kosong
            with open(os.path.join(tempDir, "settings.json"), "w") as f:
                json.dump({}, f)
                
        # 3. Ekspor catatan ke file markdown (.md)
        notesDir = os.path.join(tempDir, "notes")
        os.makedirs(notesDir, exist_ok=True)
        
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT title, content, note_type FROM notes")
        notes = cursor.fetchall()
        for note in notes:
            title = note["title"]
            content = note["content"] or ""
            note_type = note["note_type"] or "QUICK"
            
            # Buat file name yang aman
            safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
            if not safe_title:
                safe_title = "Tanpa_Judul"
            
            md_path = os.path.join(notesDir, f"{safe_title}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"---\ntype: {note_type}\n---\n\n{content}")
                
        conn.close()
        
        # 4. ZIP seluruh isi tempDir
        with zipfile.ZipFile(targetZipPath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(tempDir):
                for file in files:
                    filePath = os.path.join(root, file)
                    arcName = os.path.relpath(filePath, tempDir)
                    zipf.write(filePath, arcName)
                    
        return True
    except Exception as e:
        print(f"Error exporting workspace: {e}")
        return False
    finally:
        if os.path.exists(tempDir):
            shutil.rmtree(tempDir)

def importWorkspace(zipPath, mode="REPLACE"):
    """
    Mengimpor workspace dari berkas zip.
    Mode:
    - REPLACE: Menimpa database & settings saat ini.
    - MERGE: Menggabungkan data tasks, notes, deadlines, focus_sessions dari zip ke db saat ini.
    """
    tempDir = os.path.join(os.path.dirname(dbPath), "temp_import")
    settingsPath = getSettingsFilePath()
    
    try:
        if os.path.exists(tempDir):
            shutil.rmtree(tempDir)
        os.makedirs(tempDir, exist_ok=True)
        
        # Ekstrak ZIP
        with zipfile.ZipFile(zipPath, 'r') as zipf:
            zipf.extractall(tempDir)
            
        importedDbPath = os.path.join(tempDir, "studyos.db")
        importedSettingsPath = os.path.join(tempDir, "settings.json")
        
        if not os.path.exists(importedDbPath):
            raise FileNotFoundError("Berkas database studyos.db tidak ditemukan di dalam berkas impor.")
            
        if mode == "REPLACE":
            # Salin settings.json
            if os.path.exists(importedSettingsPath):
                shutil.copy2(importedSettingsPath, settingsPath)
            
            # Ganti file database utama (harus pastikan koneksi ditutup atau diganti langsung)
            # Karena SQLite mengizinkan penyalinan file langsung jika koneksi idle,
            # namun untuk keamanan kita timpa filenya langsung
            shutil.copy2(importedDbPath, dbPath)
            
        elif mode == "MERGE":
            # Gabungkan isi database imported ke database utama
            conn_main = getConnection()
            conn_imp = sqlite3.connect(importedDbPath)
            conn_imp.row_factory = sqlite3.Row
            
            cursor_main = conn_main.cursor()
            cursor_imp = conn_imp.cursor()
            
            # 1. Merge Tasks
            cursor_imp.execute("SELECT * FROM tasks")
            for task in cursor_imp.fetchall():
                cursor_main.execute(
                    "INSERT INTO tasks (title, subject, description, due_date, planned_date, priority, completed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (task["title"], task["subject"], task["description"], task["due_date"], task["planned_date"], task["priority"], task["completed"])
                )
                
            # 2. Merge Notes
            cursor_imp.execute("SELECT * FROM notes")
            for note in cursor_imp.fetchall():
                cursor_main.execute(
                    "INSERT INTO notes (title, content, note_type) VALUES (?, ?, ?)",
                    (note["title"], note["content"], note["note_type"])
                )
                
            # 3. Merge Focus Sessions
            cursor_imp.execute("SELECT * FROM focus_sessions")
            for session in cursor_imp.fetchall():
                cursor_main.execute(
                    "INSERT INTO focus_sessions (session_type, duration, completed, started_at, finished_at) VALUES (?, ?, ?, ?, ?)",
                    (session["session_type"], session["duration"], session["completed"], session["started_at"], session["finished_at"])
                )
                
            # 4. Merge Deadlines
            # Catatan: Karena FK merujuk ke tasks, kita hanya merge deadlines yang memiliki task valid
            # (Dalam skema penggabungan sederhana, kita ambil deadlines dari database yang diimpor)
            cursor_imp.execute("SELECT * FROM deadlines")
            for dl in cursor_imp.fetchall():
                # Cari task dengan title yang sama di main DB untuk mencocokkan task_id baru
                cursor_imp.execute("SELECT title FROM tasks WHERE id = ?", (dl["task_id"],))
                task_row = cursor_imp.fetchone()
                if task_row:
                    cursor_main.execute("SELECT id FROM tasks WHERE title = ? ORDER BY id DESC LIMIT 1", (task_row["title"],))
                    main_task = cursor_main.fetchone()
                    if main_task:
                        cursor_main.execute(
                            "INSERT INTO deadlines (task_id, deadline_date, urgency_level) VALUES (?, ?, ?)",
                            (main_task["id"], dl["deadline_date"], dl["urgency_level"])
                        )
            
            conn_main.commit()
            conn_main.close()
            conn_imp.close()
            
        return True
    except Exception as e:
        print(f"Error importing workspace: {e}")
        return False
    finally:
        if os.path.exists(tempDir):
            shutil.rmtree(tempDir)

def loadSampleProject():
    """Mengisi database dengan data sampel akademis yang realistis."""
    try:
        from core.services.TaskService import createTask
        from core.services.NoteService import createNote
        from core.services.DeadlineService import createDeadline
        from datetime import datetime, timedelta
        
        # Format tanggal relative
        today = datetime.now()
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # 1. Tambah Tasks
        t1 = createTask("Create Sidebar Navigation", "DP", "Mendesain sidebar navigasi mirip Obsidian yang collapsible.", tomorrow, today.strftime("%Y-%m-%d"), "HIGH")
        t2 = createTask("Create Planner Page", "DP", "Implementasi Notion-style database dengan Board, List, dan Calendar views.", day_after, today.strftime("%Y-%m-%d"), "HIGH")
        t3 = createTask("Create Progress Page", "DP", "Membaca data kemajuan dan menggambar grafik analitik menggunakan QPainter.", next_week, today.strftime("%Y-%m-%d"), "MEDIUM")
        t4 = createTask("Event Bus Integration", "DP", "Menghubungkan event antar-modul secara loose-coupled tanpa direct import.", None, None, "MEDIUM")
        t5 = createTask("App Startup Integration", "DP", "Konfigurasi startup dan inisialisasi window PySide6.", None, None, "LOW")
        
        # 2. Tambah Notes (dengan [[wikilinks]])
        createNote(
            "Arsitektur StudyOS",
            "StudyOS menggunakan pola Clean Architecture: UI -> Modules -> Core.\nSilakan pelajari [[Design Pattern MVC]] untuk memahami bagaimana Controller terpisah dari View.",
            "KULIAH"
        )
        createNote(
            "Design Pattern MVC",
            "Model-View-Controller digunakan untuk menjaga modularitas. View menangkap input, meneruskannya ke Controller/Handlers di modules, lalu Controller memanggil Service di core untuk memanipulasi database.",
            "KULIAH"
        )
        createNote(
            "Ide Fitur Pomodoro",
            "Menambahkan focus timer terintegrasi. Durasi 25 menit fokus, 5 menit istirahat pendek. Simpan riwayat ke focus_sessions.",
            "PERSONAL"
        )
        
        # Catat di log aktivitas
        from core.services.activity_service import logActivity
        logActivity("WORKSPACE_OPENED", "Memuat proyek sampel akademik StudyOS.")
        return True
    except Exception as e:
        print(f"Error loading sample project: {e}")
        return False
