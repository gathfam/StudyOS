from core.utils import validateRequiredString, validateChoice, validateInteger

def validateDeadlineCreation(taskId, deadlineDate, urgencyLevel):
    """Memvalidasi parameter saat pembuatan deadline baru."""
    taskId = validateInteger(taskId, "taskId", minValue=1)
    if deadlineDate is not None:
        deadlineDate = validateRequiredString(deadlineDate, "deadlineDate")
    urgencyLevel = validateChoice(urgencyLevel, ["LOW", "MEDIUM", "HIGH"], "urgencyLevel")
    return taskId, deadlineDate, urgencyLevel

def validateDeadlineUpdate(deadlineDate=None, urgencyLevel=None):
    """Memvalidasi parameter saat pembaharuan deadline."""
    validated = {}
    if deadlineDate is not None:
        validated["deadlineDate"] = validateRequiredString(deadlineDate, "deadlineDate")
    if urgencyLevel is not None:
        validated["urgencyLevel"] = validateChoice(urgencyLevel, ["LOW", "MEDIUM", "HIGH"], "urgencyLevel")
    return validated
