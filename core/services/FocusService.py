import sqlite3
from core.database import db
from core.database.queries import insertFocusSession, selectFocusSessionById, selectAllFocusSessions, deleteFocusSession as deleteFocusSessionQuery
from core.events import eventBus
from core.utils import validateInteger
from core.utils.validators import validateFocusSessionCreation, validateFocusSessionUpdate



def rowToDict(row):
    """Mengonversi sqlite3.Row ke dictionary dengan key menggunakan camelCase."""
    if not row:
        return None
    rowDict = dict(row)
    
    # Mapping dari snake_case database ke camelCase Python
    snakeToCamel = {
        "session_type": "sessionType",
        "started_at": "startedAt",
        "finished_at": "finishedAt"
    }
    
    camelDict = {}
    for key, value in rowDict.items():
        camelKey = snakeToCamel.get(key, key)
        camelDict[camelKey] = value
    return camelDict

def saveFocusSession(sessionType, duration, completed=0, startedAt=None, finishedAt=None):
    """Menyimpan sesi fokus baru ke database dan memancarkan event focusSessionSaved & pomodoroFinished."""
    # Validasi input menggunakan validator eksternal
    sessionType, duration, completed = validateFocusSessionCreation(sessionType, duration, completed)

    
    query = insertFocusSession
    
    sessionId = None
    with db.session() as cursor:
        cursor.execute(query, (sessionType, duration, completed, startedAt, finishedAt))
        sessionId = cursor.lastrowid
        
    newSession = getFocusHistory(limit=1, sessionId=sessionId)
    if newSession:
        sessionData = newSession[0]
        eventBus.emit("focusSessionSaved", sessionData)
        
        # Pemicu event khusus jika sesi Pomodoro selesai dikerjakan
        if sessionType == "POMODORO" and completed == 1:
            eventBus.emit("pomodoroFinished", sessionData)
            
        return sessionData
    return None

def getFocusHistory(limit=None, sessionId=None):
    """
    Mengambil riwayat sesi fokus dari database.
    Mendukung filter berdasarkan limit atau sessionId spesifik.
    """
    if sessionId is not None:
        query = selectFocusSessionById
        with db.session() as cursor:
            cursor.execute(query, (sessionId,))
            row = cursor.fetchone()
            return [rowToDict(row)] if row else []
            
    query = selectAllFocusSessions
    params = ()
    if limit is not None:
        limit = validateInteger(limit, "limit", minValue=1)
        query += " LIMIT ?"
        params = (limit,)
        
    with db.session() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [rowToDict(row) for row in rows]


def updateFocusSession(sessionId, sessionType=None, duration=None, completed=None, startedAt=None, finishedAt=None):
    """Memperbarui data sesi fokus di database."""
    sessionId = validateInteger(sessionId, "sessionId", minValue=1)
    
    # Ambil sesi
    history = getFocusHistory(sessionId=sessionId)
    if not history:
        raise ValueError(f"Sesi fokus dengan ID {sessionId} tidak ditemukan.")
    oldSession = history[0]
    
    updates = []
    params = []
    
    # Validasi input menggunakan validator eksternal
    validated = validateFocusSessionUpdate(sessionType, duration, completed)
    
    if sessionType is not None:
        updates.append("session_type = ?")
        params.append(validated["sessionType"])
        
    if duration is not None:
        updates.append("duration = ?")
        params.append(validated["duration"])
        
    if completed is not None:
        updates.append("completed = ?")
        params.append(validated["completed"])
        
    if startedAt is not None:
        updates.append("started_at = ?")
        params.append(startedAt)
        
    if finishedAt is not None:
        updates.append("finished_at = ?")
        params.append(finishedAt)
        
    if not updates:
        return oldSession

        
    query = f"UPDATE focus_sessions SET {', '.join(updates)} WHERE id = ?"
    params.append(sessionId)
    
    with db.session() as cursor:
        cursor.execute(query, tuple(params))
        
    updatedHistory = getFocusHistory(sessionId=sessionId)
    if updatedHistory:
        updatedSession = updatedHistory[0]
        eventBus.emit("focusSessionUpdated", updatedSession)
        
        # Pemicu khusus jika berubah jadi Pomodoro selesai
        if sessionType == "POMODORO" and completed == 1 and (oldSession["sessionType"] != "POMODORO" or oldSession["completed"] != 1):
            eventBus.emit("pomodoroFinished", updatedSession)
            
        return updatedSession
    return None

def deleteFocusSession(sessionId):
    """Menghapus sesi fokus dari database."""
    sessionId = validateInteger(sessionId, "sessionId", minValue=1)
    
    history = getFocusHistory(sessionId=sessionId)
    if not history:
        return False
    sessionToDelete = history[0]
    
    query = deleteFocusSessionQuery
    with db.session() as cursor:
        cursor.execute(query, (sessionId,))

        
    eventBus.emit("focusSessionDeleted", sessionToDelete)
    return True
