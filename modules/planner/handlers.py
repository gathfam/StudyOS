class PlannerHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleAddTaskSubmit(self, title, description):
        taskData = {
            "title": title,
            "description": description,
            "status": "pending"
        }
        self.controller.addTask(taskData)
        print(f"[PlannerHandlers] Task added successfully: '{title}' - '{description}'")

    def handleCompleteTaskClick(self, taskId):
        self.controller.completeTask(taskId)
        print(f"[PlannerHandlers] Task completed: ID {taskId}")
