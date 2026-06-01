class NotesHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleAddNoteSubmit(self, title, content, noteType):
        noteData = {
            "title": title,
            "content": content,
            "noteType": noteType
        }
        self.controller.addNote(noteData)
        print(f"[NotesHandlers] Note added successfully: '{title}'")
