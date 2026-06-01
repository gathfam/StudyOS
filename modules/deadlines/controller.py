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
        return []

    def addDeadline(self, deadlineData):
        try:
            if self.deadlineService:
                if hasattr(self.deadlineService, 'createDeadline'):
                    self.deadlineService.createDeadline(**deadlineData) if isinstance(deadlineData, dict) else self.deadlineService.createDeadline(deadlineData)
            if self.eventBus:
                self.eventBus.emit('deadlineAdded')
        except Exception as e:
            print(f"Error adding deadline: {e}")

    def updateDeadline(self, deadlineId, deadlineDate=None, urgencyLevel=None):
        try:
            if self.deadlineService and hasattr(self.deadlineService, 'updateDeadline'):
                self.deadlineService.updateDeadline(deadlineId, deadlineDate, urgencyLevel)
            if self.eventBus:
                self.eventBus.emit('deadlineUpdated')
        except Exception as e:
            print(f"Error updating deadline: {e}")

    def deleteDeadline(self, deadlineId):
        try:
            if self.deadlineService and hasattr(self.deadlineService, 'deleteDeadline'):
                self.deadlineService.deleteDeadline(deadlineId)
            if self.eventBus:
                self.eventBus.emit('deadlineDeleted')
        except Exception as e:
            print(f"Error deleting deadline: {e}")
