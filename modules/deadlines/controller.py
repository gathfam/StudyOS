class DeadlinesController:
    def __init__(self, deadline_service=None, event_bus=None):
        self.deadline_service = deadline_service
        self.event_bus = event_bus

    def loadDeadlines(self):
        if self.deadline_service:
            return self.deadline_service.get_deadlines()
        
        # Data dummy untuk keperluan testing jika deadline_service belum di-inject
        return [
            {
                "id": 1,
                "title": "Tugas Besar PBO",
                "due_date": "2026-06-15",
                "status": "open"
            },
            {
                "id": 2,
                "title": "Presentasi Proyek Akhir",
                "due_date": "2026-06-20",
                "status": "open"
            }
        ]

    def addDeadline(self, deadline_data):
        try:
            if self.deadline_service:
                self.deadline_service.create_deadline(deadline_data)
            
            if self.event_bus:
                self.event_bus.emit('deadline_added')
        except Exception as e:
            print(f"Error adding deadline: {e}")

    def completeDeadline(self, deadline_id):
        try:
            if self.deadline_service:
                self.deadline_service.complete_deadline(deadline_id)
            
            if self.event_bus:
                self.event_bus.emit('deadline_completed')
        except Exception as e:
            print(f"Error completing deadline: {e}")
