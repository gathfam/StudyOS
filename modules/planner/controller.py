# Cara Pakai di UI (PlannerPage):
# self.controller = PlannerController(taskService, eventBus)
# self.handlers = PlannerHandlers(self.controller)
# Untuk load data: self.controller.loadTasks()

class PlannerController:
    def __init__(self, taskService=None, eventBus=None):
        self.taskService = taskService
        self.eventBus = eventBus

    def loadTasks(self):
        if self.taskService and hasattr(self.taskService, 'getTask'):
            return self.taskService.getTask()
        
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
            if self.taskService and hasattr(self.taskService, 'createTask'):
                self.taskService.createTask(**taskData)
        except Exception as e:
            print(f"Error adding task: {e}")

    def completeTask(self, taskId):
        try:
            if self.taskService:
                if hasattr(self.taskService, 'completeTask'):
                    self.taskService.completeTask(taskId)
                else:
                    print("Warning: completeTask is not implemented in TaskService.")
            
            if self.eventBus:
                self.eventBus.emit('taskCompleted')
        except Exception as e:
            print(f"Error completing task: {e}")
