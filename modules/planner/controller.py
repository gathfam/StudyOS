class PlannerController:
    def __init__(self, task_service=None, event_bus=None):
        self.task_service = task_service
        self.event_bus = event_bus

    def load_tasks(self):
        if self.task_service:
            return self.task_service.get_tasks()
        
        # Dummy data untuk keperluan testing jika task_service belum di-inject
        return [
            {
                "id": 1,
                "title": "Tugas Matematika Diskrit",
                "subject": "Matematika",
                "description": "Mengerjakan soal latihan bab 1 sampai 3",
                "due_date": "2026-06-01",
                "priority": "High",
                "completed": False
            },
            {
                "id": 2,
                "title": "Review Design Pattern",
                "subject": "Software Engineering",
                "description": "Membaca kembali materi MVC dan Observer pattern",
                "due_date": "2026-06-03",
                "priority": "Medium",
                "completed": False
            }
        ]

    def add_task(self, task_data):
        try:
            if self.task_service:
                self.task_service.create_task(task_data)
            
            if self.event_bus:
                self.event_bus.emit('task_created')
        except Exception as e:
            print(f"Error adding task: {e}")

    def complete_task(self, task_id):
        try:
            if self.task_service:
                self.task_service.complete_task(task_id)
            
            if self.event_bus:
                self.event_bus.emit('task_completed')
        except Exception as e:
            print(f"Error completing task: {e}")
