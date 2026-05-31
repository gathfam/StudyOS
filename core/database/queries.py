# Task Queries
insertTask = """
INSERT INTO tasks (title, subject, description, due_date, planned_date, priority)
VALUES (?, ?, ?, ?, ?, ?)
"""

selectTaskById = "SELECT * FROM tasks WHERE id = ?"

selectAllTasks = "SELECT * FROM tasks"

updateTaskStatus = """
UPDATE tasks
SET completed = ?, updated_at = CURRENT_TIMESTAMP
WHERE id = ?
"""

deleteTask = "DELETE FROM tasks WHERE id = ?"

# Note Queries
insertNote = """
INSERT INTO notes (title, content, note_type)
VALUES (?, ?, ?)
"""

selectNoteById = "SELECT * FROM notes WHERE id = ?"

selectAllNotes = "SELECT * FROM notes"

deleteNote = "DELETE FROM notes WHERE id = ?"

# Deadline Queries
insertDeadline = """
INSERT INTO deadlines (task_id, deadline_date, urgency_level)
VALUES (?, ?, ?)
"""

selectDeadlineById = "SELECT * FROM deadlines WHERE id = ?"

selectAllDeadlines = "SELECT * FROM deadlines"

deleteDeadline = "DELETE FROM deadlines WHERE id = ?"

deleteDeadlineByTaskId = "DELETE FROM deadlines WHERE task_id = ?"

# Focus Session Queries
insertFocusSession = """
INSERT INTO focus_sessions (session_type, duration, completed, started_at, finished_at)
VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?)
"""

selectFocusSessionById = "SELECT * FROM focus_sessions WHERE id = ?"

selectAllFocusSessions = "SELECT * FROM focus_sessions ORDER BY started_at DESC"

deleteFocusSession = "DELETE FROM focus_sessions WHERE id = ?"
