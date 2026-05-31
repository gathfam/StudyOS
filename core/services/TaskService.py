import sqlite3
from core.database import db
from core.events import eventBus

def rowToDict(row):
    """Mengonversi sqlite3.Row ke dictionary dengan key menggunakan camelCase."""
    if not row:
        return None
    rowDict = dict(row)
    
    # Mapping dari snake_case database ke camelCase Python
    snakeToCamel = {
        "due_date": "dueDate",
        "planned_date": "plannedDate",
        "created_at": "createdAt",
        "updated_at": "updatedAt"
    }
    
    camelDict = {}
    for key, value in rowDict.items():
        camelKey = snakeToCamel.get(key, key)
        camelDict[camelKey] = value
    return camelDict

def createTask(title, subject=None, description=None, dueDate=None, plannedDate=None, priority="MEDIUM"):
    """Membuat task baru di database dan memancarkan event taskCreated."""
    query = """
    INSERT INTO tasks (title, subject, description, due_date, planned_date, priority)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    taskId = None
    with db.session() as cursor:
        cursor.execute(query, (title, subject, description, dueDate, plannedDate, priority))
        taskId = cursor.lastrowid
        
    newTask = getTask(taskId)
    if newTask:
        eventBus.emit("taskCreated", newTask)
    return newTask

def getTask(taskId=None):
    """
    Mengambil task dari database.
    Jika taskId diberikan, mengembalikan dictionary task tersebut (atau None jika tidak ditemukan).
    Jika taskId tidak diberikan, mengembalikan list[dict] dari semua task.
    """
    if taskId is not None:
        query = "SELECT * FROM tasks WHERE id = ?"
        with db.session() as cursor:
            cursor.execute(query, (taskId,))
            row = cursor.fetchone()
            return rowToDict(row)
    else:
        query = "SELECT * FROM tasks"
        with db.session() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [rowToDict(row) for row in rows]

if __name__ == "__main__":
    print("Testing TaskService...")
    
    # Menampung event hasil emit
    emittedTasks = []
    
    def onTaskCreated(taskData):
        print(f"Event Received! Task Created: {taskData['title']} (Priority: {taskData['priority']})")
        emittedTasks.append(taskData)
        
    # Subscribe ke event bus
    eventBus.subscribe("taskCreated", onTaskCreated)
    
    # Buat task baru untuk pengujian
    testTask = createTask(
        title="Belajar PySide6 UI",
        subject="Praktikum Pemrograman",
        description="Membuat layout mockup halaman planner",
        dueDate="2026-06-05",
        plannedDate="2026-06-01",
        priority="HIGH"
    )
    
    print("\nCreated Task Object:")
    print(testTask)
    
    # Ambil seluruh list task
    allTasks = getTask()
    print(f"\nAll Tasks (Total: {len(allTasks)}):")
    for t in allTasks:
        print(f"- {t['title']} (Due: {t['dueDate']})")
        
    # Verifikasi fungsionalitas
    if testTask and len(emittedTasks) == 1 and emittedTasks[0]["id"] == testTask["id"]:
        print("\nTaskService tests passed successfully!")
    else:
        print("\nTaskService tests failed.")
        exit(1)
