class DeadlinesHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleAddDeadlineSubmit(self, taskId, deadlineDate, urgencyLevel="MEDIUM"):
        deadlineData = {
            "taskId": taskId,
            "deadlineDate": deadlineDate,
            "urgencyLevel": urgencyLevel
        }
        self.controller.addDeadline(deadlineData)
        print(f"[DeadlinesHandlers] Deadline added successfully for task {taskId}")

    def handleDeleteDeadlineClick(self, deadlineId):
        self.controller.deleteDeadline(deadlineId)
        print(f"[DeadlinesHandlers] Deadline deleted successfully: ID '{deadlineId}'")
