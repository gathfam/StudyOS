from core.database import db
from core.events import eventBus

def logActivity(activityType, description):
    """Mencatat aktivitas baru pengguna ke dalam basis data."""
    query = "INSERT INTO activity_logs (activity_type, description) VALUES (?, ?)"
    try:
        with db.session() as cursor:
            cursor.execute(query, (activityType, description))
        
        # Pancarkan event
        eventBus.emit("activityLogged", {
            "activityType": activityType,
            "description": description
        })
        print(f"[ActivityLog] Logged: {activityType} - {description}")
    except Exception as e:
        print(f"Error logging activity: {e}")

def getActivityLog(limit=10):
    """Mengambil riwayat log aktivitas terbaru."""
    query = "SELECT * FROM activity_logs ORDER BY created_at DESC"
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
        
    try:
        with db.session() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Map database keys to Python camelCase
            logs = []
            for row in rows:
                r_dict = dict(row)
                logs.append({
                    "id": r_dict["id"],
                    "activityType": r_dict["activity_type"],
                    "description": r_dict["description"],
                    "createdAt": r_dict["created_at"]
                })
            return logs
    except Exception as e:
        print(f"Error reading activity log: {e}")
        return []

def initializeActivityListeners():
    """Mendaftarkan pendengar event untuk otomatis mencatat aktivitas."""
    def onTaskCreated(task):
        if task:
            logActivity("TASK_CREATED", f"Membuat tugas '{task.get('title')}'")
        
    def onTaskCompleted(task):
        if task:
            logActivity("TASK_COMPLETED", f"Menyelesaikan tugas '{task.get('title')}'")
        
    def onNoteCreated(note):
        if note:
            logActivity("NOTE_CREATED", f"Membuat catatan '{note.get('title')}'")
        
    def onNoteUpdated(note):
        if note:
            logActivity("NOTE_UPDATED", f"Memperbarui catatan '{note.get('title')}'")
        
    def onDeadlineAdded(deadline):
        if deadline:
            logActivity("DEADLINE_CREATED", f"Menambahkan deadline tanggal {deadline.get('deadlineDate')}")
        
    def onPomodoroFinished(session):
        if session:
            logActivity("POMODORO_COMPLETED", f"Menyelesaikan sesi fokus ({session.get('duration')} menit)")

    eventBus.subscribe("taskCreated", onTaskCreated)
    eventBus.subscribe("taskCompleted", onTaskCompleted)
    eventBus.subscribe("noteCreated", onNoteCreated)
    eventBus.subscribe("noteUpdated", onNoteUpdated)
    eventBus.subscribe("deadlineAdded", onDeadlineAdded)
    eventBus.subscribe("pomodoroFinished", onPomodoroFinished)

