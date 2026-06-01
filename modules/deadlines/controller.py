class DeadlinesController:
    def __init__(self, deadlineService=None, eventBus=None):
        self.deadlineService = deadlineService
        self.eventBus = eventBus

    def loadDeadlines(self):
        if self.deadlineService:
            if hasattr(self.deadlineService, 'getDeadlines'):
                return self.deadlineService.getDeadlines()
            elif hasattr(self.deadlineService, 'getDeadline'):
                return self.deadlineService.getDeadline()
            else:
                print("Warning: getDeadlines/getDeadline is not implemented in DeadlineService.")
        
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
                if hasattr(self.deadlineService, 'createDeadline'):
                    self.deadlineService.createDeadline(**deadlineData) if isinstance(deadlineData, dict) else self.deadlineService.createDeadline(deadlineData)
                else:
                    print("Warning: createDeadline is not implemented in DeadlineService.")
            
            if self.eventBus:
                self.eventBus.emit('deadlineAdded')
        except Exception as e:
            print(f"Error adding deadline: {e}")

    def completeDeadline(self, deadlineId):
        try:
            if self.deadlineService:
                if hasattr(self.deadlineService, 'completeDeadline'):
                    self.deadlineService.completeDeadline(deadlineId)
                else:
                    print("Warning: completeDeadline is not implemented in DeadlineService.")
            
            if self.eventBus:
                self.eventBus.emit('deadlineCompleted')
        except Exception as e:
            print(f"Error completing deadline: {e}")
