# Cara Pakai di UI (PlannerPage):
# self.controller = PlannerController(taskService, eventBus)
# self.handlers = PlannerHandlers(self.controller)
# Untuk load data: self.controller.loadTasks()

class PlannerController:
    def __init__(self, taskService=None, eventBus=None):
        self.taskService = taskService
        self.eventBus = eventBus

    def loadTasks(self):
        if self.taskService:
            return self.taskService.getTasks()
        
        # Dummy data untuk keperluan testing jika taskService belum di-inject
        return [
            {
                "id": 1,
                "title": "Tugas Matematika Diskrit",
                "subject": "Matematika",
                "description": "Mengerjakan soal latihan bab 1 sampai 3",
                "dueDate": "2026-06-01",
                "priority": "High",
                "completed": False
            },
            {
                "id": 2,
                "title": "Review Design Pattern",
                "subject": "Software Engineering",
                "description": "Membaca kembali materi MVC dan Observer pattern",
                "dueDate": "2026-06-03",
                "priority": "Medium",
                "completed": False
            }
        ]

    def addTask(self, taskData):
        try:
            if self.taskService:
                self.taskService.createTask(taskData)
            
            if self.eventBus:
                self.eventBus.emit('taskCreated')
        except Exception as e:
            print(f"Error adding task: {e}")

    def completeTask(self, taskId):
        try:
            if self.taskService:
                self.taskService.completeTask(taskId)
            
            if self.eventBus:
                self.eventBus.emit('taskCompleted')
        except Exception as e:
            print(f"Error completing task: {e}")
