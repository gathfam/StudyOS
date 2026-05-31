import sqlite3
from typing import overload, Union, List, Dict, Any, Optional
from core.database import db
from core.database.queries import insertNote, selectNoteById, selectAllNotes, deleteNote as deleteNoteQuery
from core.events import eventBus
from core.utils import validateInteger
from core.utils.validators import validateNoteCreation, validateNoteUpdate





def rowToDict(row):
    """Mengonversi sqlite3.Row ke dictionary dengan key menggunakan camelCase."""
    if not row:
        return None
    rowDict = dict(row)
    
    # Mapping dari snake_case database ke camelCase Python
    snakeToCamel = {
        "note_type": "noteType",
        "created_at": "createdAt",
        "updated_at": "updatedAt"
    }
    
    camelDict = {}
    for key, value in rowDict.items():
        camelKey = snakeToCamel.get(key, key)
        camelDict[camelKey] = value
    return camelDict

def createNote(title, content=None, noteType="QUICK"):
    """Membuat note baru di database dan memancarkan event noteCreated."""
    # Validasi input
    title = validateNoteCreation(title)

    query = insertNote
    
    noteId = None
    with db.session() as cursor:
        cursor.execute(query, (title, content, noteType))
        noteId = cursor.lastrowid
        
    newNote = getNote(noteId)
    if newNote:
        eventBus.emit("noteCreated", newNote)
    return newNote

@overload
def getNote() -> List[Dict[str, Any]]: ...

@overload
def getNote(noteId: int) -> Optional[Dict[str, Any]]: ...

def getNote(noteId: Optional[int] = None) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:

    """
    Mengambil note dari database.
    Jika noteId diberikan, mengembalikan dictionary note tersebut (atau None jika tidak ditemukan).
    Jika noteId tidak diberikan, mengembalikan list[dict] dari semua note.
    """
    if noteId is not None:
        query = selectNoteById
        with db.session() as cursor:
            cursor.execute(query, (noteId,))
            row = cursor.fetchone()
            return rowToDict(row)
    else:
        query = selectAllNotes
        with db.session() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [rowToDict(row) for row in rows]


def updateNote(noteId, title=None, content=None, noteType=None):
    """Memperbarui catatan di database."""
    noteId = validateInteger(noteId, "noteId", minValue=1)
    
    oldNote = getNote(noteId)
    if not oldNote:
        raise ValueError(f"Catatan dengan ID {noteId} tidak ditemukan.")
        
    updates = []
    params = []
    
    # Validasi input menggunakan validator eksternal
    validated = validateNoteUpdate(title)
    
    if title is not None:
        updates.append("title = ?")
        params.append(validated["title"])
        
    if content is not None:
        updates.append("content = ?")
        params.append(content)
        
    if noteType is not None:
        from core.utils import validateRequiredString
        noteType = validateRequiredString(noteType, "noteType")
        updates.append("note_type = ?")
        params.append(noteType)
        
    if not updates:
        return oldNote

        
    updates.append("updated_at = CURRENT_TIMESTAMP")
    query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
    params.append(noteId)
    
    with db.session() as cursor:
        cursor.execute(query, tuple(params))
        
    updatedNote = getNote(noteId)
    if updatedNote:
        eventBus.emit("noteUpdated", updatedNote)
    return updatedNote

def deleteNote(noteId):
    """Menghapus catatan dari database."""
    noteId = validateInteger(noteId, "noteId", minValue=1)
    
    noteToDelete = getNote(noteId)
    if not noteToDelete:
        return False
        
    query = deleteNoteQuery
    with db.session() as cursor:
        cursor.execute(query, (noteId,))

        
    eventBus.emit("noteDeleted", noteToDelete)
    return True

