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

    def handleUpdateNoteSubmit(self, noteId, title, content, noteType):
        noteData = {
            "title": title,
            "content": content,
            "noteType": noteType
        }
        self.controller.updateNote(noteId, noteData)
        print(f"[NotesHandlers] Note updated successfully: ID '{noteId}'")

    def handleDeleteNoteClick(self, noteId):
        self.controller.deleteNote(noteId)
        print(f"[NotesHandlers] Note deleted successfully: ID '{noteId}'")
