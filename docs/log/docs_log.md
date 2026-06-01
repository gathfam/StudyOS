# StudyOS Core Architecture & Documentation Log

Dokumen ini menjelaskan struktur, implementasi teknis, dan alasan arsitektural pembuatan modul-modul di dalam direktori `core/`.

---

## 1. core/database/connection.py & __init__.py (Database Connection)
*   **Fitur Utama**: Manajemen Koneksi SQLite & Session Handler.
*   **Implementasi Teknis**: Menggunakan library bawaan `sqlite3` dan `contextlib.contextmanager`. Berisi fungsi `getConnection()` untuk mengembalikan objek koneksi SQLite yang terkonfigurasi dengan `row_factory = sqlite3.Row` (agar data kolom bisa diakses sebagai key/mapping) serta mengaktifkan *foreign key enforce* (`PRAGMA foreign_keys = ON;`). Kelas `DatabaseManager` menyediakan `session()` berbasis context manager untuk membungkus query dalam transaksi atomik (`commit`/`rollback`).
*   **Alasan & Maksud (Why)**: Untuk menyediakan jalur akses database yang aman, konsisten, dan terpusat. Masalah transaksi SQL (seperti kegagalan commit yang menyebabkan database terkunci atau korup) diselesaikan secara transparan oleh context manager `session`.
*   **Komunikasi & Flow**: Modul Service (`TaskService`) mengimpor `db` (singleton) dari package ini untuk mengeksekusi query database.

---

## 2. core/database/schema.py (Database Schema)
*   **Fitur Utama**: Skema Database & Auto-Initialization.
*   **Implementasi Teknis**: Berisi fungsi `initializeDatabase()` yang menyimpan daftar query SQL DDL (`CREATE TABLE IF NOT EXISTS`) untuk 5 tabel utama StudyOS (`tasks`, `deadlines`, `notes`, `focus_sessions`, `progress_stats`). Fungsi ini dipanggil secara lokal dan otomatis pada saat modul database pertama kali di-import.
*   **Alasan & Maksud (Why)**: Memisahkan skema DDL dari logika manajemen koneksi untuk menghindari ketergantungan melingkar (*circular imports*). Membantu menjaga agar proses awal inisialisasi tabel bersifat deklaratif dan idempotent (aman dipanggil berulang kali).
*   **Komunikasi & Flow**: Dipanggil secara internal oleh `DatabaseManager` di `connection.py` pada saat inisialisasi awal.

---

## 3. core/events/event_bus.py & __init__.py (Event Bus System)
*   **Fitur Utama**: Sistem Publish-Subscribe.
*   **Implementasi Teknis**: Berisi kelas `EventBus` (dengan alias `EvenBust`) yang melacak callback terdaftar menggunakan dictionary internal `self.listeners`. Menyediakan fungsi `subscribe(eventType, callback)` untuk mendaftarkan fungsi pendengar, dan `emit(eventType, *args, **kwargs)` untuk memicu pemanggilan seluruh callback terdaftar. Di-ekspos sebagai objek *singleton* `eventBus`.
*   **Alasan & Maksud (Why)**: Menyelesaikan masalah *tight-coupling* (ketergantungan erat) antar-modul. Modul A tidak perlu secara langsung mengimpor Modul B untuk mengirim data; ia cukup memancarkan event, dan modul manapun yang tertarik dapat mendengarkannya secara independen.
*   **Komunikasi & Flow**: Modul Service (`TaskService`) memanggil `eventBus.emit("taskCreated", taskData)` setelah task baru tersimpan. Modul UI (`ui/`) atau modul fitur lainnya (`modules/`) akan melakukan `subscribe()` ke event bus untuk mendeteksi perubahan data dan memperbarui tampilan UI secara otomatis.

---

## 4. core/services/TaskService.py & __init__.py (Task Service)
*   **Fitur Utama**: Logika Bisnis & CRUD Tugas.
*   **Implementasi Teknis**: Mengintegrasikan database dan event bus. Berisi fungsi `createTask()` untuk memasukkan tugas ke SQLite menggunakan parameter query aman (`?`), memanggil `eventBus.emit()`, dan mengembalikan dictionary task baru. Fungsi `getTask()` mengembalikan satu task jika `taskId` diisi, atau list dari seluruh task (`list[dict]`) jika kosong. Fungsi helper `rowToDict()` mengonversi `sqlite3.Row` database menjadi dictionary Python dengan penamaan kunci camelCase (`dueDate`, `plannedDate`, `createdAt`, `updatedAt`).
*   **Alasan & Maksud (Why)**: Menyediakan lapisan abstraksi logika bisnis (*Service Layer*) di atas database. Komponen UI tidak boleh melakukan query SQL langsung; melainkan memanggil fungsi-fungsi tingkat tinggi dari Service ini untuk menjamin konsistensi data dan kelancaran alur logika (seperti pengiriman event).
*   **Komunikasi & Flow**: Dipanggil oleh lapisan pengontrol/presenter di dalam `modules/` atau langsung oleh widget di `ui/`. Menggunakan `core.database.db` untuk akses SQL dan `core.events.eventBus` untuk notifikasi event.

---

## 5. core/__init__.py (Core Initialization Gateway)
*   **Fitur Utama**: Startup App Gateway.
*   **Implementasi Teknis**: Menyediakan fungsi tunggal `startup()` yang mengimpor dan menjalankan `initializeDatabase()`.
*   **Alasan & Maksud (Why)**: Menyediakan titik masuk tunggal bagi aplikasi utama (seperti `main.py`) untuk memicu persiapan seluruh komponen di lapisan `core/` saat aplikasi dijalankan.
*   **Komunikasi & Flow**: Dipanggil saat inisialisasi aplikasi pertama kali (di tingkat startup script root).
