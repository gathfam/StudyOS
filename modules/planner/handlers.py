class PlannerHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleAddTaskSubmit(self, title, description):
        task_data = {
            "title": title,
            "description": description,
            "status": "pending"
        }
        self.controller.addTask(task_data)
        print(f"[PlannerHandlers] Task added successfully: '{title}' - '{description}'")

    def handleCompleteTaskClick(self, task_id):
        self.controller.completeTask(task_id)
        print(f"[PlannerHandlers] Task completed: ID {task_id}")
