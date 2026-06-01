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
        return []

    def addTask(self, taskData):
        try:
            if self.taskService and hasattr(self.taskService, 'createTask'):
                self.taskService.createTask(**taskData)
        except Exception as e:
            print(f"Error adding task: {e}")

    def updateTaskStatus(self, taskId, completed):
        try:
            if self.taskService and hasattr(self.taskService, 'updateTaskStatus'):
                self.taskService.updateTaskStatus(taskId, completed)
        except Exception as e:
            print(f"Error updating task status: {e}")

    def deleteTask(self, taskId):
        try:
            if self.taskService and hasattr(self.taskService, 'deleteTask'):
                self.taskService.deleteTask(taskId)
        except Exception as e:
            print(f"Error deleting task: {e}")
