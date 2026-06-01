import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, QSize

from core.events import eventBus
from core.services.activity_service import getActivityLog
import core.services.TaskService as TaskService
import core.services.NoteService as NoteService
import core.services.DeadlineService as DeadlineService
from modules.planner.controller import PlannerController
from modules.deadlines.controller import DeadlinesController
from modules.notes.controller import NotesController

class DashboardPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        
        self.plannerController = PlannerController(taskService=TaskService, eventBus=eventBus)
        self.deadlinesController = DeadlinesController(deadlineService=DeadlineService, eventBus=eventBus)
        self.notesController = NotesController(noteService=NoteService, eventBus=eventBus)
        
        # Subscribe to Event Bus
        eventBus.subscribe("taskCreated", self.refresh_dashboard)
        eventBus.subscribe("taskUpdated", self.refresh_dashboard)
        eventBus.subscribe("taskCompleted", self.refresh_dashboard)
        eventBus.subscribe("noteCreated", self.refresh_dashboard)
        eventBus.subscribe("noteUpdated", self.refresh_dashboard)
        eventBus.subscribe("noteDeleted", self.refresh_dashboard)
        eventBus.subscribe("activityLogged", self.refresh_dashboard)
        
        self.accent_color = "#BCA7FF"
        self.init_ui()
        self.refresh_dashboard()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Title
        header_layout = QHBoxLayout()
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        self.title_label = QLabel("Dashboard")
        self.title_label.setObjectName("appTitle")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        self.date_label = QLabel(datetime.now().strftime("%A, %d %B %Y").upper())
        self.date_label.setStyleSheet("color: #8B8B92; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.date_label)
        header_layout.addWidget(title_widget, 1)
        main_layout.addLayout(header_layout)

        # Split into columns (Left: Recommended + Focus, Right: Tasks + Deadlines + Activity)
        grid = QGridLayout()
        grid.setSpacing(15)
        main_layout.addLayout(grid)

        # ==========================================
        # LEFT COLUMN
        # ==========================================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # 1. Recommended Next Action Panel (Obsidian/Linear styling)
        self.rec_widget = QFrame()
        self.rec_widget.setObjectName("leftPanel")
        self.rec_widget.setStyleSheet(f"#leftPanel {{ border-left: 3px solid {self.accent_color}; background-color: #141416; border-top: 1px solid #252529; border-right: 1px solid #252529; border-bottom: 1px solid #252529; border-radius: 4px; }}")
        rec_layout = QVBoxLayout(self.rec_widget)
        rec_layout.setContentsMargins(15, 15, 15, 15)
        rec_layout.setSpacing(6)
        
        self.rec_header = QLabel("RECOMMENDED NEXT ACTION")
        self.rec_header.setStyleSheet("color: #8B8B92; font-weight: bold; font-size: 9px; letter-spacing: 0.8px;")
        rec_layout.addWidget(self.rec_header)
        
        self.rec_title = QLabel("No tasks found")
        self.rec_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #ffffff;")
        self.rec_title.setWordWrap(True)
        rec_layout.addWidget(self.rec_title)
        
        self.rec_detail = QLabel("Your workspace is empty or all tasks are finished.")
        self.rec_detail.setStyleSheet("color: #8B8B92; font-size: 11px;")
        self.rec_detail.setWordWrap(True)
        rec_layout.addWidget(self.rec_detail)
        
        self.rec_meta_layout = QHBoxLayout()
        self.rec_meta_layout.setSpacing(10)
        
        self.rec_priority_label = QLabel("Priority: Normal")
        self.rec_priority_label.setStyleSheet("color: #8B8B92; font-size: 11px;")
        
        self.rec_due_label = QLabel("Due: Today")
        self.rec_due_label.setStyleSheet("color: #8B8B92; font-size: 11px;")
        
        self.rec_meta_layout.addWidget(self.rec_priority_label)
        self.rec_meta_layout.addWidget(self.rec_due_label)
        self.rec_meta_layout.addStretch()
        
        self.btn_start_rec = QPushButton("Start Working")
        self.btn_start_rec.setObjectName("btnPrimaryAccent")
        self.btn_start_rec.setStyleSheet("QPushButton { font-size: 11px; padding: 4px 10px; }")
        self.btn_start_rec.clicked.connect(self.run_recommended_action)
        self.rec_meta_layout.addWidget(self.btn_start_rec)
        
        rec_layout.addLayout(self.rec_meta_layout)
        left_layout.addWidget(self.rec_widget)

        # 2. Focus Status (Pomodoro)
        self.pomo_widget = QFrame()
        self.pomo_widget.setObjectName("leftPanel")
        self.pomo_widget.setStyleSheet("#leftPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
        pomo_layout = QVBoxLayout(self.pomo_widget)
        pomo_layout.setContentsMargins(15, 15, 15, 15)
        pomo_layout.setSpacing(6)
        
        pomo_header = QLabel("FOCUS TIMER")
        pomo_header.setStyleSheet("color: #8B8B92; font-weight: bold; font-size: 9px; letter-spacing: 0.8px;")
        pomo_layout.addWidget(pomo_header)
        
        h_pomo_body = QHBoxLayout()
        self.pomo_timer_lbl = QLabel("25:00")
        self.pomo_timer_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; font-family: monospace;")
        h_pomo_body.addWidget(self.pomo_timer_lbl)
        
        self.pomo_task_lbl = QLabel("Independent Study")
        self.pomo_task_lbl.setStyleSheet("color: #8B8B92; font-size: 12px;")
        h_pomo_body.addWidget(self.pomo_task_lbl, 1)
        
        self.btn_quick_pomo = QPushButton("Timer")
        self.btn_quick_pomo.setStyleSheet("QPushButton { font-size: 11px; padding: 4px 10px; }")
        self.btn_quick_pomo.clicked.connect(self.go_to_pomodoro)
        h_pomo_body.addWidget(self.btn_quick_pomo)
        
        pomo_layout.addLayout(h_pomo_body)
        left_layout.addWidget(self.pomo_widget)
        
        left_layout.addStretch()
        grid.addWidget(left_widget, 0, 0)

        # ==========================================
        # RIGHT COLUMN
        # ==========================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # 1. Upcoming Deadlines Section
        self.dl_widget = QFrame()
        self.dl_widget.setObjectName("rightPanel")
        self.dl_widget.setStyleSheet("#rightPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
        dl_layout = QVBoxLayout(self.dl_widget)
        dl_layout.setContentsMargins(15, 15, 15, 15)
        dl_layout.setSpacing(6)
        
        dl_header = QLabel("UPCOMING DEADLINES")
        dl_header.setStyleSheet("color: #8B8B92; font-weight: bold; font-size: 9px; letter-spacing: 0.8px;")
        dl_layout.addWidget(dl_header)
        
        self.dl_list = QListWidget()
        self.dl_list.setMinimumHeight(80)
        self.dl_list.setMaximumHeight(100)
        self.dl_list.setStyleSheet("QListWidget::item { background-color: transparent; border: none; padding: 4px 0px; }")
        dl_layout.addWidget(self.dl_list)
        
        self.dl_empty = QLabel("No deadlines found.")
        self.dl_empty.setStyleSheet("color: #8B8B92; font-style: italic; font-size: 11px; padding: 5px 0;")
        dl_layout.addWidget(self.dl_empty)
        right_layout.addWidget(self.dl_widget)

        # 2. Active Tasks Section
        self.tasks_box = QFrame()
        self.tasks_box.setObjectName("rightPanel")
        self.tasks_box.setStyleSheet("#rightPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
        tasks_lay = QVBoxLayout(self.tasks_box)
        tasks_lay.setContentsMargins(15, 15, 15, 15)
        tasks_lay.setSpacing(6)
        
        tasks_header = QLabel("ACTIVE TASKS")
        tasks_header.setStyleSheet("color: #8B8B92; font-weight: bold; font-size: 9px; letter-spacing: 0.8px;")
        tasks_lay.addWidget(tasks_header)
        
        self.tasks_list = QListWidget()
        self.tasks_list.setMinimumHeight(80)
        self.tasks_list.setMaximumHeight(100)
        self.tasks_list.setStyleSheet("QListWidget::item { background-color: transparent; border: none; padding: 4px 0px; }")
        self.tasks_list.itemClicked.connect(self.on_task_clicked)
        tasks_lay.addWidget(self.tasks_list)
        
        self.tasks_empty = QLabel("No active tasks.")
        self.tasks_empty.setStyleSheet("color: #8B8B92; font-style: italic; font-size: 11px; padding: 5px 0;")
        tasks_lay.addWidget(self.tasks_empty)
        right_layout.addWidget(self.tasks_box)

        # 3. Recent Activity Section
        self.act_box = QFrame()
        self.act_box.setObjectName("rightPanel")
        self.act_box.setStyleSheet("#rightPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
        act_lay = QVBoxLayout(self.act_box)
        act_lay.setContentsMargins(15, 15, 15, 15)
        act_lay.setSpacing(6)
        
        act_header = QLabel("ACTIVITY FEED")
        act_header.setStyleSheet("color: #8B8B92; font-weight: bold; font-size: 9px; letter-spacing: 0.8px;")
        act_lay.addWidget(act_header)
        
        self.act_list = QListWidget()
        self.act_list.setMinimumHeight(80)
        self.act_list.setMaximumHeight(100)
        self.act_list.setStyleSheet("QListWidget::item { background-color: transparent; border: none; padding: 4px 0px; }")
        act_lay.addWidget(self.act_list)
        
        self.act_empty = QLabel("No activity recorded.")
        self.act_empty.setStyleSheet("color: #8B8B92; font-style: italic; font-size: 11px; padding: 5px 0;")
        act_lay.addWidget(self.act_empty)
        right_layout.addWidget(self.act_box)

        right_layout.addStretch()
        grid.addWidget(right_widget, 0, 1)

        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 6)

    def refresh_dashboard(self, *args, **kwargs):
        """Fetches SQLite details and updates lists."""
        tasks = self.plannerController.loadTasks() or []
        deadlines = self.deadlinesController.loadDeadlines() or []
        logs = getActivityLog(limit=5) or []

        # 1. Update Recommended Task
        self.update_recommended_task(tasks)
        
        # 2. Update Deadlines
        self.dl_list.clear()
        pending_deadlines = [d for d in deadlines]
        if pending_deadlines:
            self.dl_empty.setVisible(False)
            self.dl_list.setVisible(True)
            for dl in pending_deadlines[:3]:
                task_title = "Deadline"
                associated_task = next((t for t in tasks if t["id"] == dl["taskId"]), None)
                if associated_task:
                    task_title = associated_task["title"]
                    
                item = QListWidgetItem(f"{task_title} (Due: {dl.get('deadlineDate')})")
                item.setData(Qt.ItemDataRole.UserRole, dl)
                self.dl_list.addItem(item)
        else:
            self.dl_empty.setVisible(True)
            self.dl_list.setVisible(False)

        # 3. Update Active Tasks
        self.tasks_list.clear()
        active_tasks = [t for t in tasks if t.get("completed") == 0]
        if active_tasks:
            self.tasks_empty.setVisible(False)
            self.tasks_list.setVisible(True)
            for t in active_tasks[:3]:
                item = QListWidgetItem(f"{t['title']}")
                item.setData(Qt.ItemDataRole.UserRole, t)
                self.tasks_list.addItem(item)
        else:
            self.tasks_empty.setVisible(True)
            self.tasks_list.setVisible(False)

        # 4. Update Activity Logs
        self.act_list.clear()
        if logs:
            self.act_empty.setVisible(False)
            self.act_list.setVisible(True)
            for log in logs:
                desc = log["description"]
                time_str = log["createdAt"].split(" ")[-1] if " " in log["createdAt"] else ""
                item = QListWidgetItem(f"{desc} \t ({time_str})")
                self.act_list.addItem(item)
        else:
            self.act_empty.setVisible(True)
            self.act_list.setVisible(False)

    def update_recommended_task(self, tasks):
        """Deterministic priority: Overdue -> Today -> High Prio -> In Progress -> Oldest."""
        pending_tasks = [t for t in tasks if t.get("completed") == 0]
        if not pending_tasks:
            self.rec_title.setText("No pending tasks")
            self.rec_detail.setText("All tasks and academic projects completed successfully.")
            self.rec_priority_label.setVisible(False)
            self.rec_due_label.setVisible(False)
            self.btn_start_rec.setVisible(False)
            self.rec_widget.setStyleSheet(f"#leftPanel {{ border-left: 3px solid #8B8B92; background-color: #141416; border-top: 1px solid #252529; border-right: 1px solid #252529; border-bottom: 1px solid #252529; border-radius: 4px; }}")
            return

        self.rec_priority_label.setVisible(True)
        self.rec_due_label.setVisible(True)
        self.btn_start_rec.setVisible(True)
        
        now_str = datetime.now().strftime("%Y-%m-%d")
        
        overdue_tasks = []
        today_tasks = []
        high_priority = []
        in_progress = []
        
        for t in pending_tasks:
            due = t.get("dueDate")
            priority = t.get("priority", "MEDIUM")
            planned = t.get("plannedDate")
            
            if due:
                if due < now_str:
                    overdue_tasks.append(t)
                elif due == now_str:
                    today_tasks.append(t)
            
            if priority == "HIGH":
                high_priority.append(t)
                
            if planned:
                in_progress.append(t)

        recommended = None
        status_msg = ""
        border_color = self.accent_color
        
        if overdue_tasks:
            recommended = sorted(overdue_tasks, key=lambda x: x.get("dueDate", ""))[0]
            status_msg = "Overdue task. Action required."
            border_color = "#E57373" # Red
        elif today_tasks:
            recommended = sorted(today_tasks, key=lambda x: x.get("priority", ""))[0]
            status_msg = "Due today."
            border_color = "#F2C66D" # Amber
        elif high_priority:
            recommended = high_priority[0]
            status_msg = "High priority action item."
            border_color = "#F2C66D" # Amber
        elif in_progress:
            recommended = in_progress[0]
            status_msg = "Active in-progress task."
            border_color = "#7FC97F" # Green
        else:
            recommended = pending_tasks[0]
            status_msg = "Next task in queue."
            border_color = self.accent_color

        self.recommended_task_obj = recommended
        self.rec_title.setText(recommended["title"])
        self.rec_detail.setText(f"{status_msg}\n{recommended.get('description', 'No description.')}")
        
        self.rec_priority_label.setText(f"Priority: {recommended.get('priority', 'MEDIUM')}")
        due_date = recommended.get("dueDate")
        self.rec_due_label.setText(f"Due: {due_date}" if due_date else "Due: None")
        
        # Apply left border coloring dynamically
        self.rec_widget.setStyleSheet(f"#leftPanel {{ border-left: 3px solid {border_color}; background-color: #141416; border-top: 1px solid #252529; border-right: 1px solid #252529; border-bottom: 1px solid #252529; border-radius: 4px; }}")

    def run_recommended_action(self):
        if hasattr(self, "recommended_task_obj") and self.recommended_task_obj:
            if self.mainWindow:
                self.mainWindow.navigate_to("Planner")
                
    def on_task_clicked(self, item):
        task = item.data(Qt.ItemDataRole.UserRole)
        if task and self.mainWindow:
            self.mainWindow.navigate_to("Planner")

    def go_to_pomodoro(self):
        if self.mainWindow:
            self.mainWindow.navigate_to("Pomodoro")
            
    def update_accent(self, color):
        self.accent_color = color
        self.btn_start_rec.setStyleSheet(f"QPushButton {{ background-color: {color}; color: #0B0B0C; font-size: 11px; padding: 4px 10px; }}")
        self.refresh_dashboard()
