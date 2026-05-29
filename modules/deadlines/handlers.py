class DeadlinesHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleDeadlineSubmit(self, title, dueDate):
        deadlineData = {
            "title": title,
            "dueDate": dueDate,
            "status": "open"
        }
        self.controller.addDeadline(deadlineData)
        print(f"[DeadlinesHandlers] Deadline added successfully: '{title}'")

    def handleCompleteDeadlineClick(self, deadlineId):
        self.controller.completeDeadline(deadlineId)
        print(f"[DeadlinesHandlers] Deadline completed successfully: ID '{deadlineId}'")
