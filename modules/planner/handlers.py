class PlannerHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleAddTaskSubmit(self, title, subject=None, description=None, dueDate=None, plannedDate=None, priority="MEDIUM"):
        taskData = {
            "title": title,
            "subject": subject,
            "description": description,
            "dueDate": dueDate,
            "plannedDate": plannedDate,
            "priority": priority
        }
        self.controller.addTask(taskData)
        print(f"[PlannerHandlers] Task added successfully: '{title}'")

    def handleUpdateTaskStatusClick(self, taskId, completed):
        self.controller.updateTaskStatus(taskId, completed)
        print(f"[PlannerHandlers] Task status updated: ID {taskId} - Completed: {completed}")

    def handleDeleteTaskClick(self, taskId):
        self.controller.deleteTask(taskId)
        print(f"[PlannerHandlers] Task deleted: ID {taskId}")
