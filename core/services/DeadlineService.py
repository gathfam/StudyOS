import sqlite3
from typing import overload, Union, List, Dict, Any, Optional
from core.database import db
from core.database.queries import insertDeadline, selectDeadlineById, selectAllDeadlines, deleteDeadline as deleteDeadlineQuery, deleteDeadlineByTaskId as deleteDeadlineByTaskIdQuery
from core.events import eventBus
from core.utils import validateInteger
from core.utils.validators import validateDeadlineCreation, validateDeadlineUpdate




def rowToDict(row):
    """Mengonversi sqlite3.Row ke dictionary dengan key menggunakan camelCase."""
    if not row:
        return None
    rowDict = dict(row)
    
    # Mapping dari snake_case database ke camelCase Python
    snakeToCamel = {
        "task_id": "taskId",
        "deadline_date": "deadlineDate",
        "urgency_level": "urgencyLevel",
        "created_at": "createdAt"
    }
    
    camelDict = {}
    for key, value in rowDict.items():
        camelKey = snakeToCamel.get(key, key)
        camelDict[camelKey] = value
    return camelDict

def createDeadline(taskId, deadlineDate=None, urgencyLevel="MEDIUM"):
    """Membuat deadline baru di database dan memancarkan event deadlineAdded."""
    # Validasi input menggunakan validator eksternal
    taskId, deadlineDate, urgencyLevel = validateDeadlineCreation(taskId, deadlineDate, urgencyLevel)
    
    if deadlineDate is None:
        # Ikuti due date dari task
        from core.services.TaskService import getTask
        task = getTask(taskId)
        if not task:
            raise ValueError(f"Task dengan ID {taskId} tidak ditemukan.")
        
        taskDueDate = task.get("dueDate")
        if not taskDueDate:
            raise ValueError(f"Task dengan ID {taskId} tidak memiliki dueDate untuk dijadikan deadline.")
        deadlineDate = taskDueDate

        
    query = insertDeadline
    
    deadlineId = None
    with db.session() as cursor:
        cursor.execute(query, (taskId, deadlineDate, urgencyLevel))
        deadlineId = cursor.lastrowid
        
    newDeadline = getDeadline(deadlineId)
    if newDeadline:
        eventBus.emit("deadlineAdded", newDeadline)
    return newDeadline


@overload
def getDeadline() -> List[Dict[str, Any]]: ...

@overload
def getDeadline(deadlineId: int) -> Optional[Dict[str, Any]]: ...

def getDeadline(deadlineId: Optional[int] = None) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:

    """
    Mengambil deadline dari database.
    Jika deadlineId diberikan, mengembalikan dictionary deadline tersebut (atau None jika tidak ditemukan).
    Jika deadlineId tidak diberikan, mengembalikan list[dict] dari semua deadline.
    """
    if deadlineId is not None:
        query = selectDeadlineById
        with db.session() as cursor:
            cursor.execute(query, (deadlineId,))
            row = cursor.fetchone()
            return rowToDict(row)
    else:
        query = selectAllDeadlines
        with db.session() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [rowToDict(row) for row in rows]


def deleteDeadline(deadlineId):
    """Menghapus deadline berdasarkan deadlineId."""
    deadlineId = validateInteger(deadlineId, "deadlineId", minValue=1)
    query = deleteDeadlineQuery
    with db.session() as cursor:
        cursor.execute(query, (deadlineId,))
    eventBus.emit("deadlineDeleted", {"id": deadlineId})

def deleteDeadlineByTaskId(taskId):
    """Menghapus seluruh deadline yang terasosiasi dengan taskId."""
    taskId = validateInteger(taskId, "taskId", minValue=1)
    query = deleteDeadlineByTaskIdQuery
    with db.session() as cursor:
        cursor.execute(query, (taskId,))

    eventBus.emit("deadlinesDeletedForTask", {"taskId": taskId})

def updateDeadline(deadlineId, deadlineDate=None, urgencyLevel=None):
    """Memperbarui data deadline di database."""
    deadlineId = validateInteger(deadlineId, "deadlineId", minValue=1)
    
    oldDeadline = getDeadline(deadlineId)
    if not oldDeadline:
        raise ValueError(f"Deadline dengan ID {deadlineId} tidak ditemukan.")
        
    updates = []
    params = []
    
    # Validasi input menggunakan validator eksternal
    validated = validateDeadlineUpdate(deadlineDate, urgencyLevel)
    
    if deadlineDate is not None:
        updates.append("deadline_date = ?")
        params.append(validated["deadlineDate"])
        
    if urgencyLevel is not None:
        updates.append("urgency_level = ?")
        params.append(validated["urgencyLevel"])
        
    if not updates:
        return oldDeadline

        
    query = f"UPDATE deadlines SET {', '.join(updates)} WHERE id = ?"
    params.append(deadlineId)
    
    with db.session() as cursor:
        cursor.execute(query, tuple(params))
        
    updatedDeadline = getDeadline(deadlineId)
    if updatedDeadline:
        eventBus.emit("deadlineUpdated", updatedDeadline)
    return updatedDeadline

if __name__ == "__main__":


    print("Testing DeadlineService...")
    
    # Menampung event hasil emit
    emittedDeadlines = []
    
    def onDeadlineAdded(deadlineData):
        print(f"Event Received! Deadline Added: Task {deadlineData['taskId']} due {deadlineData['deadlineDate']}!")
        emittedDeadlines.append(deadlineData)
        
    # Subscribe ke event bus
    eventBus.subscribe("deadlineAdded", onDeadlineAdded)
    
    # Kita butuh task_id yang valid. Untuk test ini, kita buat task dummy dulu jika belum ada, atau pakai ID 1.
    # Karena foreign key ON, kita pastikan task ID 1 ada di DB.
    try:
        from core.services.TaskService import createTask, getTask
        # Pastikan ada task dengan id=1 untuk FK constraint
        task = getTask(1)
        if not task:
            createTask(title="Task Dummy untuk Test FK", priority="MEDIUM")
    except Exception as e:
        print(f"Warning setting up dummy task: {e}")
    
    # Buat deadline baru untuk pengujian
    testDeadline = createDeadline(
        taskId=1,
        deadlineDate="2026-06-15",
        urgencyLevel="HIGH"
    )
    
    print("\nCreated Deadline Object:")
    print(testDeadline)
    
    # Ambil seluruh list deadline
    allDeadlines = getDeadline()
    print(f"\nAll Deadlines (Total: {len(allDeadlines)}):")
    for d in allDeadlines:
        print(f"- Task ID: {d['taskId']} (Due: {d['deadlineDate']}, Urgency: {d['urgencyLevel']})")
        
    # Verifikasi fungsionalitas
    if testDeadline and len(emittedDeadlines) == 1 and emittedDeadlines[0]["id"] == testDeadline["id"]:
        print("\nDeadlineService tests passed successfully!")
    else:
        print("\nDeadlineService tests failed.")
        exit(1)
