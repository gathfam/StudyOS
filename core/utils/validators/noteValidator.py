from core.utils import validateRequiredString

def validateNoteCreation(title):
    """Memvalidasi parameter saat pembuatan catatan baru."""
    title = validateRequiredString(title, "title")
    return title

def validateNoteUpdate(title=None):
    """Memvalidasi parameter saat pembaharuan catatan."""
    validated = {}
    if title is not None:
        validated["title"] = validateRequiredString(title, "title")
    return validated
