from core.utils import validateRequiredString, validateChoice, validateInteger

def validateTaskCreation(title, priority):
    """Memvalidasi parameter saat pembuatan task baru."""
    title = validateRequiredString(title, "title")
    priority = validateChoice(priority, ["LOW", "MEDIUM", "HIGH"], "priority")
    return title, priority

def validateTaskUpdate(title=None, priority=None, completed=None):
    """Memvalidasi parameter saat pembaharuan task."""
    validated = {}
    if title is not None:
        validated["title"] = validateRequiredString(title, "title")
    if priority is not None:
        validated["priority"] = validateChoice(priority, ["LOW", "MEDIUM", "HIGH"], "priority")
    if completed is not None:
        # Jika bertipe boolean, konversi ke integer
        if isinstance(completed, bool):
            validated["completed"] = 1 if completed else 0
        else:
            validated["completed"] = validateChoice(completed, [0, 1], "completed")
    return validated
