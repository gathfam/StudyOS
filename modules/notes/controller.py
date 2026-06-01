class NotesController:
    def __init__(self, noteService=None, eventBus=None):
        self.noteService = noteService
        self.eventBus = eventBus

    def loadNotes(self):
        if self.noteService:
            # Mengambil data menggunakan service yang di-inject
            if hasattr(self.noteService, 'getNotes'):
                return self.noteService.getNotes()
            elif hasattr(self.noteService, 'getNote'):
                return self.noteService.getNote()
            else:
                print("Warning: getNotes/getNote is not implemented in NoteService.")
        
        return []

    def addNote(self, noteData):
        try:
            if self.noteService:
                if hasattr(self.noteService, 'createNote'):
                    self.noteService.createNote(**noteData) if isinstance(noteData, dict) else self.noteService.createNote(noteData)
                else:
                    print("Warning: createNote is not implemented in NoteService.")
            
            if self.eventBus:
                self.eventBus.emit('noteCreated')
        except Exception as e:
            print(f"Error adding note: {e}")

    def updateNote(self, noteId, noteData):
        try:
            if self.noteService:
                if hasattr(self.noteService, 'updateNote'):
                    self.noteService.updateNote(noteId, **noteData) if isinstance(noteData, dict) else self.noteService.updateNote(noteId, noteData)
                else:
                    print("Warning: updateNote is not implemented in NoteService.")
            
            if self.eventBus:
                self.eventBus.emit('noteUpdated')
        except Exception as e:
            print(f"Error updating note: {e}")

    def deleteNote(self, noteId):
        try:
            if self.noteService:
                if hasattr(self.noteService, 'deleteNote'):
                    self.noteService.deleteNote(noteId)
                else:
                    print("Warning: deleteNote is not implemented in NoteService.")
            
            if self.eventBus:
                self.eventBus.emit('noteDeleted')
        except Exception as e:
            print(f"Error deleting note: {e}")
