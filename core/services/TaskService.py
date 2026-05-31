import sqlite3
from typing import overload, Union, List, Dict, Any, Optional
from core.database import db
from core.database.queries import insertTask, selectTaskById, selectAllTasks, updateTaskStatus as updateTaskStatusQuery, deleteTask as deleteTaskQuery

from core.events import eventBus
from core.utils import validateInteger
from core.utils.validators import validateTaskCreation, validateTaskUpdate





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
    # Validasi input
    title, priority = validateTaskCreation(title, priority)

    
    query = insertTask


    
    taskId = None
    with db.session() as cursor:
        cursor.execute(query, (title, subject, description, dueDate, plannedDate, priority))
        taskId = cursor.lastrowid
        
    newTask = getTask(taskId)
    if newTask:
        eventBus.emit("taskCreated", newTask)
        # Jika task memiliki due date, otomatis buat deadline terkait
        if newTask.get("dueDate"):
            try:
                from core.services.DeadlineService import createDeadline
                createDeadline(taskId=newTask["id"], deadlineDate=newTask["dueDate"], urgencyLevel="MEDIUM")
            except Exception as e:
                pass
    return newTask


@overload
def getTask() -> List[Dict[str, Any]]: ...

@overload
def getTask(taskId: int) -> Optional[Dict[str, Any]]: ...

def getTask(taskId: Optional[int] = None) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:

    """
    Mengambil task dari database.
    Jika taskId diberikan, mengembalikan dictionary task tersebut (atau None jika tidak ditemukan).
    Jika taskId tidak diberikan, mengembalikan list[dict] dari semua task.
    """
    if taskId is not None:
        query = selectTaskById
        with db.session() as cursor:
            cursor.execute(query, (taskId,))
            row = cursor.fetchone()
            return rowToDict(row)
    else:
        query = selectAllTasks
        with db.session() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [rowToDict(row) for row in rows]

def updateTaskStatus(taskId, completed):
    """Memperbarui status selesai (completed) dari task."""
    taskId = validateInteger(taskId, "taskId", minValue=1)
    
    # Konversi bool ke int jika perlu
    if isinstance(completed, bool):
        completedVal = 1 if completed else 0
    else:
        completedVal = validateChoice(completed, [0, 1], "completed")
        
    query = updateTaskStatusQuery

    with db.session() as cursor:
        cursor.execute(query, (completedVal, taskId))

        
    # Hapus deadline jika task selesai (completedVal == 1)
    if completedVal == 1:
        try:
            from core.services.DeadlineService import deleteDeadlineByTaskId
            deleteDeadlineByTaskId(taskId)
        except Exception as e:
            pass
            
    # Ambil task ter-update untuk dikembalikan dan emit event
    updatedTask = getTask(taskId)
    if updatedTask:
        eventBus.emit("taskUpdated", updatedTask)
        if completedVal == 1:
            eventBus.emit("taskCompleted", updatedTask)
            
    return updatedTask

def updateTask(taskId, title=None, subject=None, description=None, dueDate=None, plannedDate=None, priority=None, completed=None):
    """Memperbarui informasi task di database dan menyelaraskan dengan deadline."""
    taskId = validateInteger(taskId, "taskId", minValue=1)
    
    # Ambil data task saat ini
    oldTask = getTask(taskId)
    if not oldTask:
        raise ValueError(f"Task dengan ID {taskId} tidak ditemukan.")
        
    # Buat query dinamis berdasarkan parameter yang dikirim (tidak None)
    updates = []
    params = []
    
    # Validasi input menggunakan validator eksternal
    validated = validateTaskUpdate(title, priority, completed)
    completedVal = validated.get("completed", oldTask["completed"])
    
    if title is not None:
        updates.append("title = ?")
        params.append(validated["title"])
        
    if subject is not None:
        updates.append("subject = ?")
        params.append(subject)
        
    if description is not None:
        updates.append("description = ?")
        params.append(description)
        
    if dueDate is not None:
        # dueDate bisa diisi string tanggal atau None untuk menghapusnya
        if dueDate != "":
            from core.utils import validateRequiredString
            dueDate = validateRequiredString(dueDate, "dueDate")
        else:
            dueDate = None
        updates.append("due_date = ?")
        params.append(dueDate)
        
    if plannedDate is not None:
        updates.append("planned_date = ?")
        params.append(plannedDate)
        
    if priority is not None:
        updates.append("priority = ?")
        params.append(validated["priority"])
        
    if completed is not None:
        updates.append("completed = ?")
        params.append(completedVal)

        
    if not updates:
        return oldTask # Tidak ada perubahan
        
    updates.append("updated_at = CURRENT_TIMESTAMP")
    
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    params.append(taskId)
    
    with db.session() as cursor:
        cursor.execute(query, tuple(params))
        
    # Ambil data task ter-update
    updatedTask = getTask(taskId)
    if not updatedTask:
        return None
        
    # Penyelarasan dengan Deadline:
    # 1. Jika completed disetel 1, otomatis hapus deadline
    if completedVal == 1:
        try:
            from core.services.DeadlineService import deleteDeadlineByTaskId
            deleteDeadlineByTaskId(taskId)
        except Exception:
            pass
    # 2. Jika dueDate berubah (dan task belum selesai)
    elif dueDate is not None and completedVal == 0:
        try:
            from core.services.DeadlineService import getDeadline, createDeadline, deleteDeadlineByTaskId
            # Cek apakah sudah ada deadline untuk task ini
            deadlines = getDeadline()
            taskDeadlines = [d for d in deadlines if d["taskId"] == taskId]
            
            if dueDate is None:
                # Jika dueDate dihapus, hapus deadline terkait
                deleteDeadlineByTaskId(taskId)
            elif taskDeadlines:
                # Jika sudah ada, update deadline pertama
                from core.services.DeadlineService import updateDeadline
                updateDeadline(taskDeadlines[0]["id"], deadlineDate=dueDate)
            else:
                # Jika belum ada, buat baru
                createDeadline(taskId=taskId, deadlineDate=dueDate, urgencyLevel="MEDIUM")
        except Exception:
            pass
            
    eventBus.emit("taskUpdated", updatedTask)
    if completedVal == 1 and oldTask["completed"] == 0:
        eventBus.emit("taskCompleted", updatedTask)
        
    return updatedTask

def deleteTask(taskId):
    """Menghapus task dari database (akan men-cascade hapus deadline terkait)."""
    taskId = validateInteger(taskId, "taskId", minValue=1)
    
    # Simpan info task sebelum dihapus untuk dikirim lewat event
    taskToDelete = getTask(taskId)
    if not taskToDelete:
        return False
        
    query = deleteTaskQuery
    with db.session() as cursor:
        cursor.execute(query, (taskId,))

        
    eventBus.emit("taskDeleted", taskToDelete)
    return True

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
