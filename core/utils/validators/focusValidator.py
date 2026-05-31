from core.utils import validateChoice, validateInteger

def validateFocusSessionCreation(sessionType, duration, completed):
    """Memvalidasi parameter saat penyimpanan sesi fokus baru."""
    sessionType = validateChoice(sessionType, ["POMODORO", "SHORT_BREAK", "LONG_BREAK"], "sessionType")
    duration = validateInteger(duration, "duration", minValue=1)
    completed = validateChoice(completed, [0, 1], "completed")
    return sessionType, duration, completed

def validateFocusSessionUpdate(sessionType=None, duration=None, completed=None):
    """Memvalidasi parameter saat pembaharuan sesi fokus."""
    validated = {}
    if sessionType is not None:
        validated["sessionType"] = validateChoice(sessionType, ["POMODORO", "SHORT_BREAK", "LONG_BREAK"], "sessionType")
    if duration is not None:
        validated["duration"] = validateInteger(duration, "duration", minValue=1)
    if completed is not None:
        validated["completed"] = validateChoice(completed, [0, 1], "completed")
    return validated
