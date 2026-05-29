class NotesController:
    def __init__(self, note_service=None, event_bus=None):
        self.note_service = note_service
        self.event_bus = event_bus

    def loadNotes(self):
        if self.note_service:
            # Mengambil data menggunakan service yang di-inject
            return self.note_service.get_notes()
        
        # Data dummy jika note_service belum di-inject (keperluan testing)
        return [
            {
                "id": 1,
                "title": "Design Pattern: MVC",
                "content": "MVC memisahkan aplikasi menjadi 3 komponen: Model, View, dan Controller untuk modularitas.",
                "note_type": "kuliah",
                "created_at": "2026-05-28 09:00:00"
            },
            {
                "id": 2,
                "title": "Ide Fitur Tambahan",
                "content": "Mungkin kita bisa menambahkan fitur Pomodoro di fase selanjutnya.",
                "note_type": "personal",
                "created_at": "2026-05-29 10:30:00"
            }
        ]

    def addNote(self, note_data):
        try:
            if self.note_service:
                self.note_service.create_note(note_data)
            
            if self.event_bus:
                self.event_bus.emit('note_created')
        except Exception as e:
            print(f"Error adding note: {e}")
