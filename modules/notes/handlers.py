class NotesHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleAddNoteSubmit(self, title, content, note_type):
        note_data = {
            "title": title,
            "content": content,
            "note_type": note_type
        }
        self.controller.addNote(note_data)
        print(f"[NotesHandlers] Note added successfully: '{title}'")
