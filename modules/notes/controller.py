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
        
        # Data dummy jika noteService belum di-inject (keperluan testing)
        return [
            {
                "id": 1,
                "title": "Design Pattern: MVC",
                "content": "MVC memisahkan aplikasi menjadi 3 komponen: Model, View, dan Controller untuk modularitas.",
                "noteType": "kuliah",
                "createdAt": "2026-05-28 09:00:00"
            },
            {
                "id": 2,
                "title": "Ide Fitur Tambahan",
                "content": "Mungkin kita bisa menambahkan fitur Pomodoro di fase selanjutnya.",
                "noteType": "personal",
                "createdAt": "2026-05-29 10:30:00"
            }
        ]

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
