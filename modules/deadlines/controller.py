class DeadlinesController:
    def __init__(self, deadlineService=None, eventBus=None):
        self.deadlineService = deadlineService
        self.eventBus = eventBus

    def loadDeadlines(self):
        if self.deadlineService:
            return self.deadlineService.getDeadlines()
        
        # Data dummy untuk keperluan testing jika deadlineService belum di-inject
        return [
            {
                "id": 1,
                "title": "Tugas Besar PBO",
                "dueDate": "2026-06-15",
                "status": "open"
            },
            {
                "id": 2,
                "title": "Presentasi Proyek Akhir",
                "dueDate": "2026-06-20",
                "status": "open"
            }
        ]

    def addDeadline(self, deadlineData):
        try:
            if self.deadlineService:
                self.deadlineService.createDeadline(deadlineData)
            
            if self.eventBus:
                self.eventBus.emit('deadlineAdded')
        except Exception as e:
            print(f"Error adding deadline: {e}")

    def completeDeadline(self, deadlineId):
        try:
            if self.deadlineService:
                self.deadlineService.completeDeadline(deadlineId)
            
            if self.eventBus:
                self.eventBus.emit('deadlineCompleted')
        except Exception as e:
            print(f"Error completing deadline: {e}")
