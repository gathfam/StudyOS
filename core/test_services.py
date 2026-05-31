import unittest
import os
import sqlite3

# Import core modules
import core
from core.database import dbName, dbPath, getConnection, db
from core.events import eventBus
from core.services import (
    createTask, getTask, updateTaskStatus, updateTask, deleteTask,
    createNote, getNote, updateNote, deleteNote,
    createDeadline, getDeadline, updateDeadline, deleteDeadline,
    saveFocusSession, getFocusHistory, updateFocusSession, deleteFocusSession
)



class TestCoreServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Menjalankan startup aplikasi dan mempersiapkan database."""
        core.startup()

    def test_01_event_bus(self):
        """Menguji EventBus: registrasi callback dan pemancaran event."""
        testResults = []
        
        def testCallback(data):
            testResults.append(data)
            
        eventBus.subscribe("testEvent", testCallback)
        eventBus.emit("testEvent", {"status": "SUCCESS"})
        
        self.assertEqual(len(testResults), 1)
        self.assertEqual(testResults[0]["status"], "SUCCESS")
        
        # Test unsubscribe
        eventBus.unsubscribe("testEvent", testCallback)
        eventBus.emit("testEvent", {"status": "FAIL"})
        self.assertEqual(len(testResults), 1)

    def test_02_task_service(self):
        """Menguji TaskService: pembuatan task, pencarian, status update, dan auto-deadline."""
        # 1. Valid Input (Otomatis membuat deadline karena ada dueDate)
        task = createTask(
            title="Tugas Pemrograman Terapan",
            subject="DP",
            description="Mengerjakan Modul Core",
            dueDate="2026-06-02",
            plannedDate="2026-06-01",
            priority="HIGH"
        )
        self.assertIsNotNone(task)
        self.assertEqual(task["title"], "Tugas Pemrograman Terapan")
        self.assertEqual(task["priority"], "HIGH")
        self.assertEqual(task["completed"], 0)
        
        # Verifikasi bahwa deadline dibuat secara otomatis
        deadlines = getDeadline()
        taskDeadlines = [d for d in deadlines if d["taskId"] == task["id"]]
        self.assertEqual(len(taskDeadlines), 1)
        self.assertEqual(taskDeadlines[0]["deadlineDate"], "2026-06-02")
        
        # 2. Get Single Task
        fetched = getTask(task["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["title"], task["title"])
        
        # 3. Get All Tasks
        allTasks = getTask()
        self.assertTrue(len(allTasks) >= 1)
        
        # 4. Update Status Selesai (Completed = 1) -> Harus menghapus deadline terkait
        updated = updateTaskStatus(task["id"], completed=True)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["completed"], 1)
        
        # Verifikasi deadline terhapus setelah task selesai
        deadlinesAfter = getDeadline()
        taskDeadlinesAfter = [d for d in deadlinesAfter if d["taskId"] == task["id"]]
        self.assertEqual(len(taskDeadlinesAfter), 0)
        
        # 5. Validation: Empty Title
        with self.assertRaises(ValueError):
            createTask(title="")
            
        # 6. Validation: Invalid Priority Choice
        with self.assertRaises(ValueError):
            createTask(title="Valid Title", priority="VERY_HIGH")


    def test_03_note_service(self):
        """Menguji NoteService: pembuatan note, pencarian, dan validasi."""
        # 1. Valid Input
        note = createNote(
            title="Catatan Teori Clean Architecture",
            content="Lapisan core tidak boleh mengimpor UI.",
            noteType="QUICK"
        )
        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "Catatan Teori Clean Architecture")
        
        # 2. Get Note
        fetched = getNote(note["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["content"], note["content"])
        
        # 3. Validation: Empty Title
        with self.assertRaises(ValueError):
            createNote(title="   ")

    def test_04_deadline_service(self):
        """Menguji DeadlineService: pembuatan deadline, pencarian, dan validasi."""
        # Pastikan ada task dengan ID 1 untuk FK constraint
        task = getTask(1)
        if not task:
            task = createTask(title="Task untuk FK Deadline", priority="MEDIUM")
            
        # 1. Valid Input (Manual Date)
        deadline = createDeadline(
            taskId=task["id"],
            deadlineDate="2026-06-15",
            urgencyLevel="HIGH"
        )
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline["taskId"], task["id"])
        self.assertEqual(deadline["urgencyLevel"], "HIGH")
        self.assertEqual(deadline["deadlineDate"], "2026-06-15")
        
        # 2. Get Deadline
        fetched = getDeadline(deadline["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["deadlineDate"], deadline["deadlineDate"])
        
        # 3. Valid Input (Inherit Task Due Date)
        # Pastikan task memiliki dueDate
        taskWithDue = createTask(title="Task dengan Due Date", dueDate="2026-07-20")
        deadlineAuto = createDeadline(
            taskId=taskWithDue["id"],
            deadlineDate=None,
            urgencyLevel="MEDIUM"
        )
        self.assertIsNotNone(deadlineAuto)
        self.assertEqual(deadlineAuto["deadlineDate"], "2026-07-20")
        
        # 4. Validation: Task has no Due Date
        taskWithoutDue = createTask(title="Task Tanpa Due Date", dueDate=None)
        with self.assertRaises(ValueError):
            createDeadline(taskId=taskWithoutDue["id"], deadlineDate=None)
            
        # 5. Validation: Invalid Task ID
        with self.assertRaises(ValueError):
            createDeadline(taskId=-5, deadlineDate="2026-06-15", urgencyLevel="LOW")
            
        # 6. Validation: Invalid Urgency Level
        with self.assertRaises(ValueError):
            createDeadline(taskId=task["id"], deadlineDate="2026-06-15", urgencyLevel="URGENT")


    def test_05_focus_service(self):
        """Menguji FocusService: penyimpanan sesi, riwayat, dan validasi."""
        # 1. Valid Input
        session = saveFocusSession(
            sessionType="POMODORO",
            duration=25,
            completed=1
        )
        self.assertIsNotNone(session)
        self.assertEqual(session["sessionType"], "POMODORO")
        self.assertEqual(session["duration"], 25)
        self.assertEqual(session["completed"], 1)
        
        # 2. Get History
        history = getFocusHistory(limit=2)
        self.assertTrue(len(history) >= 1)
        self.assertEqual(history[0]["sessionType"], "POMODORO")
        
        # 3. Validation: Invalid Session Type
        with self.assertRaises(ValueError):
            saveFocusSession(sessionType="WORK", duration=25)
            
        # 4. Validation: Duration Zero/Negative
        with self.assertRaises(ValueError):
            saveFocusSession(sessionType="POMODORO", duration=0)
            
        # 5. Validation: Invalid Completed Flag
        with self.assertRaises(ValueError):
            saveFocusSession(sessionType="POMODORO", duration=25, completed=2)

    def test_06_updates_and_deletions(self):
        """Menguji pembaruan (update) dan penghapusan (delete) pada seluruh service."""
        # 1. Test Task Update & Delete
        task = createTask(title="Task Awal", priority="LOW")
        updated_task = updateTask(task["id"], title="Task Diubah", priority="HIGH")
        self.assertEqual(updated_task["title"], "Task Diubah")
        self.assertEqual(updated_task["priority"], "HIGH")
        
        self.assertTrue(deleteTask(task["id"]))
        self.assertIsNone(getTask(task["id"]))
        
        # 2. Test Note Update & Delete
        note = createNote(title="Note Awal", content="Awal")
        updated_note = updateNote(note["id"], title="Note Diubah", content="Diubah")
        self.assertEqual(updated_note["title"], "Note Diubah")
        self.assertEqual(updated_note["content"], "Diubah")
        
        self.assertTrue(deleteNote(note["id"]))
        self.assertIsNone(getNote(note["id"]))
        
        # 3. Test Deadline Update & Delete
        temp_task = createTask(title="Task Temp", dueDate="2026-08-01")
        # Deadline otomatis dibuat karena ada dueDate
        deadlines = getDeadline()
        task_deadlines = [d for d in deadlines if d["taskId"] == temp_task["id"]]
        self.assertEqual(len(task_deadlines), 1)
        deadline_id = task_deadlines[0]["id"]
        
        updated_deadline = updateDeadline(deadline_id, deadlineDate="2026-08-15", urgencyLevel="HIGH")
        self.assertEqual(updated_deadline["deadlineDate"], "2026-08-15")
        self.assertEqual(updated_deadline["urgencyLevel"], "HIGH")
        
        deleteDeadline(deadline_id)
        self.assertIsNone(getDeadline(deadline_id))
        deleteTask(temp_task["id"])
        
        # 4. Test Focus Session Update & Delete
        session = saveFocusSession(sessionType="POMODORO", duration=25)
        updated_session = updateFocusSession(session["id"], duration=30, completed=1)
        self.assertEqual(updated_session["duration"], 30)
        self.assertEqual(updated_session["completed"], 1)
        
        self.assertTrue(deleteFocusSession(session["id"]))
        history = getFocusHistory(sessionId=session["id"])
        self.assertEqual(len(history), 0)

if __name__ == "__main__":
    unittest.main()

