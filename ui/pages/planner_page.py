import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QComboBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QCursor

import core.services.TaskService as TaskService
from core.events import eventBus
from modules.planner.controller import PlannerController
from modules.planner.handlers import PlannerHandlers

class TaskCard(QFrame):
    """Linear-inspired minimalist Task card using thin left-border for priority."""
    def __init__(self, task, parent=None, plannerHandlers=None):
        super().__init__(parent)
        self.task = task
        self.plannerHandlers = plannerHandlers
        self.setObjectName("taskCard")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        priority = self.task.get("priority", "MEDIUM")
        border_color = self.get_prio_color(priority)
        
        # Style card: flat surface, thin left border, minimal padding
        self.setStyleSheet(f"""
            #taskCard {{
                background-color: #141416;
                border-top: 1px solid #252529;
                border-right: 1px solid #252529;
                border-bottom: 1px solid #252529;
                border-left: 3px solid {border_color};
                border-radius: 3px;
            }}
        """)

        # Title Row
        h_row = QHBoxLayout()
        h_row.setSpacing(6)
        self.title_lbl = QLabel(self.task["title"])
        self.title_lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #F2F2F2;")
        self.title_lbl.setWordWrap(True)
        h_row.addWidget(self.title_lbl, 1)

        # Subtle options trigger
        self.btn_opt = QPushButton("•••")
        self.btn_opt.setFixedSize(18, 16)
        self.btn_opt.setStyleSheet("QPushButton { border: none; background: transparent; color: #8B8B92; font-size: 8px; } QPushButton:hover { color: #ffffff; }")
        self.btn_opt.clicked.connect(self.show_options_menu)
        h_row.addWidget(self.btn_opt)
        layout.addLayout(h_row)

        # Subject & Info
        meta_parts = []
        if self.task.get("subject"):
            meta_parts.append(self.task["subject"])
        if self.task.get("dueDate"):
            meta_parts.append(self.task["dueDate"])
            
        if meta_parts:
            meta_lbl = QLabel(" | ".join(meta_parts))
            meta_lbl.setStyleSheet("color: #8B8B92; font-size: 10px;")
            layout.addWidget(meta_lbl)

    def get_prio_color(self, priority):
        colors = {
            "HIGH": "#E57373",   # Red
            "MEDIUM": "#F2C66D", # Amber
            "LOW": "#7FC97F"     # Green
        }
        return colors.get(priority, "#8B8B92")

    def show_options_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #141416;
                border: 1px solid #252529;
                color: #F2F2F2;
            }
            QMenu::item:selected {
                background-color: #1A1A1D;
                color: #BCA7FF;
            }
        """)
        
        completed = self.task.get("completed", 0)
        planned = self.task.get("plannedDate")
        
        if completed == 1:
            act_reopen = menu.addAction("Move to To Do")
            act_reopen.triggered.connect(lambda: self.move_task("TODO"))
        else:
            if planned:
                act_todo = menu.addAction("Move to To Do")
                act_todo.triggered.connect(lambda: self.move_task("TODO"))
                act_complete = menu.addAction("Move to Completed")
                act_complete.triggered.connect(lambda: self.move_task("COMPLETED"))
            else:
                act_progress = menu.addAction("Move to In Progress")
                act_progress.triggered.connect(lambda: self.move_task("PROGRESS"))
                act_complete = menu.addAction("Move to Completed")
                act_complete.triggered.connect(lambda: self.move_task("COMPLETED"))
                
        menu.addSeparator()
        act_del = menu.addAction("Delete Task")
        act_del.triggered.connect(self.delete_task)
        
        menu.exec(QCursor.pos())

    def move_task(self, target):
        if not self.plannerHandlers:
            return
            
        task_id = self.task["id"]
        if target == "TODO":
            TaskService.updateTask(task_id, completed=0, plannedDate="")
        elif target == "PROGRESS":
            today_str = datetime.now().strftime("%Y-%m-%d")
            TaskService.updateTask(task_id, completed=0, plannedDate=today_str)
        elif target == "COMPLETED":
            self.plannerHandlers.handleUpdateTaskStatusClick(task_id, 1)

    def delete_task(self):
        reply = QMessageBox.question(
            self, "Delete Task",
            f"Are you sure you want to delete '{self.task['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes and self.plannerHandlers:
            self.plannerHandlers.handleDeleteTaskClick(self.task["id"])


class PlannerPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.controller = PlannerController(taskService=TaskService, eventBus=eventBus)
        self.handlers = PlannerHandlers(controller=self.controller)
        
        # Subscribe
        eventBus.subscribe("taskCreated", self.refresh_view)
        eventBus.subscribe("taskUpdated", self.refresh_view)
        eventBus.subscribe("taskDeleted", self.refresh_view)
        eventBus.subscribe("taskCompleted", self.refresh_view)
        
        self.current_view = "BOARD"
        self.accent_color = "#BCA7FF"
        self.init_ui()
        self.refresh_view()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)

        # Header Row (Minimal, Typography-First)
        h_header = QHBoxLayout()
        title_widget = QWidget()
        v_title = QVBoxLayout(title_widget)
        v_title.setContentsMargins(0, 0, 0, 0)
        v_title.setSpacing(2)
        
        self.title_lbl = QLabel("Planner")
        self.title_lbl.setObjectName("appTitle")
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        subtitle = QLabel("Manage tasks, projects, and execution flow")
        subtitle.setObjectName("appSubtitle")
        subtitle.setStyleSheet("color: #8B8B92; font-size: 11px;")
        v_title.addWidget(self.title_lbl)
        v_title.addWidget(subtitle)
        h_header.addWidget(title_widget, 1)

        # View Selector & Add Button
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Board", "List", "Calendar"])
        self.view_combo.currentIndexChanged.connect(self.on_view_changed)
        self.view_combo.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        h_header.addWidget(self.view_combo)

        self.btn_new_task = QPushButton("+ Task")
        self.btn_new_task.setObjectName("btnPrimaryAccent")
        self.btn_new_task.setStyleSheet("QPushButton { font-size: 11px; padding: 4px 10px; }")
        self.btn_new_task.clicked.connect(self.open_quick_add_task)
        h_header.addWidget(self.btn_new_task)
        
        self.main_layout.addLayout(h_header)

        # Container
        self.container_scroll = QScrollArea()
        self.container_scroll.setWidgetResizable(True)
        self.container_scroll.setObjectName("mainContentSurface")
        self.container_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.main_layout.addWidget(self.container_scroll)

    def on_view_changed(self, index):
        views = ["BOARD", "LIST", "CALENDAR"]
        self.current_view = views[index]
        self.refresh_view()

    def refresh_view(self, *args, **kwargs):
        tasks = self.controller.loadTasks() or []
        old_widget = self.container_scroll.takeWidget()
        if old_widget:
            old_widget.deleteLater()
            
        if self.current_view == "BOARD":
            self.render_board_view(tasks)
        elif self.current_view == "LIST":
            self.render_list_view(tasks)
        elif self.current_view == "CALENDAR":
            self.render_calendar_view(tasks)

    def render_board_view(self, tasks):
        board = QWidget()
        board_layout = QHBoxLayout(board)
        board_layout.setSpacing(12)
        board_layout.setContentsMargins(0, 0, 0, 0)

        todo_tasks = []
        progress_tasks = []
        completed_tasks = []
        
        for t in tasks:
            if t.get("completed") == 1:
                completed_tasks.append(t)
            else:
                planned = t.get("plannedDate")
                if planned and planned.strip():
                    progress_tasks.append(t)
                else:
                    todo_tasks.append(t)

        columns = [
            ("Backlog", todo_tasks, "#8B8B92"),
            ("In Progress", progress_tasks, "#BCA7FF"),
            ("Completed", completed_tasks, "#7FC97F")
        ]

        for col_title, col_tasks, indicator_color in columns:
            col_frame = QFrame()
            col_frame.setStyleSheet("QFrame { background-color: #141416; border-radius: 4px; border: 1px solid #252529; }")
            col_layout = QVBoxLayout(col_frame)
            col_layout.setContentsMargins(10, 10, 10, 10)
            col_layout.setSpacing(8)

            # Col Head (Minimal, monochrome)
            lbl_title = QLabel(f"<b>{col_title.upper()}</b>   <font color='#8B8B92'>{len(col_tasks)}</font>")
            lbl_title.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
            col_layout.addWidget(lbl_title)

            # Column border accent strip
            divider = QFrame()
            divider.setFixedHeight(2)
            divider.setStyleSheet(f"background-color: {indicator_color}; border: none;")
            col_layout.addWidget(divider)

            list_widget = QListWidget()
            list_widget.setStyleSheet("""
                QListWidget { background: transparent; border: none; }
                QListWidget::item { background: transparent; border: none; padding: 0px; margin-bottom: 6px; }
            """)
            col_layout.addWidget(list_widget)

            if not col_tasks:
                empty = QLabel("Empty")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty.setStyleSheet("color: #8B8B92; font-style: italic; font-size: 11px; padding: 15px 0;")
                col_layout.addWidget(empty)
            else:
                for task in col_tasks:
                    item = QListWidgetItem()
                    card = TaskCard(task, plannerHandlers=self.handlers)
                    item.setSizeHint(card.sizeHint())
                    list_widget.addItem(item)
                    list_widget.setItemWidget(item, card)

            col_layout.addStretch()
            board_layout.addWidget(col_frame)

        self.container_scroll.setWidget(board)

    def render_list_view(self, tasks):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Task Name", "Subject", "Priority", "Due Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.setObjectName("plannerTable")
        table.setStyleSheet("""
            QTableWidget {
                background-color: #141416;
                border: 1px solid #252529;
                border-radius: 4px;
                gridline-color: #252529;
            }
            QHeaderView::section {
                background-color: #1A1A1D;
                color: #8B8B92;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        table.setRowCount(len(tasks))
        for row, t in enumerate(tasks):
            # ID
            id_item = QTableWidgetItem(str(t["id"]))
            id_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row, 0, id_item)

            # Title
            title_item = QTableWidgetItem(t["title"])
            title_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if t.get("completed") == 1:
                title_item.setForeground(QColor("#8B8B92"))
            table.setItem(row, 1, title_item)

            # Subject
            sub_item = QTableWidgetItem(t.get("subject") or "-")
            sub_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row, 2, sub_item)

            # Priority
            prio = t.get("priority", "MEDIUM")
            prio_item = QTableWidgetItem(prio)
            prio_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if prio == "HIGH":
                prio_item.setForeground(QColor("#E57373"))
            elif prio == "MEDIUM":
                prio_item.setForeground(QColor("#F2C66D"))
            else:
                prio_item.setForeground(QColor("#7FC97F"))
            table.setItem(row, 3, prio_item)

            # Due Date
            due_item = QTableWidgetItem(t.get("dueDate") or "-")
            due_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(row, 4, due_item)

        self.container_scroll.setWidget(table)

    def render_calendar_view(self, tasks):
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        calendar_layout.setContentsMargins(0, 0, 0, 0)

        grid = QGridLayout()
        grid.setSpacing(6)
        calendar_layout.addLayout(grid)

        # Days Header
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            lbl = QLabel(day.upper())
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #8B8B92; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;")
            grid.addWidget(lbl, 0, col)

        today = datetime.now()
        start_of_month = datetime(today.year, today.month, 1)
        start_day_idx = start_of_month.weekday()
        current_date = start_of_month - timedelta(days=start_day_idx)

        for row in range(1, 7):
            for col in range(7):
                day_box = QFrame()
                day_box.setMinimumHeight(65)
                
                is_curr_month = current_date.month == today.month
                box_bg = "#141416" if is_curr_month else "#0B0B0C"
                border = "1px solid #252529" if is_curr_month else "1px solid #141416"
                
                day_box.setStyleSheet(f"QFrame {{ background-color: {box_bg}; border: {border}; border-radius: 4px; }}")
                box_lay = QVBoxLayout(day_box)
                box_lay.setContentsMargins(4, 4, 4, 4)
                
                # Date Label
                date_num = QLabel(str(current_date.day))
                num_color = "#F2F2F2" if is_curr_month else "#52525b"
                if current_date.date() == today.date():
                    num_color = self.accent_color
                    date_num.setStyleSheet("font-weight: bold;")
                date_num.setStyleSheet(f"color: {num_color}; font-size: 10px;")
                box_lay.addWidget(date_num)

                # Tasks Due
                date_str = current_date.strftime("%Y-%m-%d")
                due_tasks = [t for t in tasks if t.get("dueDate") == date_str and t.get("completed") == 0]
                
                if due_tasks:
                    task_dots = QWidget()
                    dots_lay = QHBoxLayout(task_dots)
                    dots_lay.setContentsMargins(0, 0, 0, 0)
                    dots_lay.setSpacing(2)
                    
                    for t in due_tasks[:3]:
                        dot = QLabel("●")
                        prio = t.get("priority", "MEDIUM")
                        color = "#E57373" if prio == "HIGH" else ("#F2C66D" if prio == "MEDIUM" else "#7FC97F")
                        dot.setStyleSheet(f"color: {color}; font-size: 8px; border: none; background: transparent;")
                        dots_lay.addWidget(dot)
                    
                    dots_lay.addStretch()
                    box_lay.addWidget(task_dots)
                    
                    task_titles = "\n".join([f"- {t['title']}" for t in due_tasks])
                    day_box.setToolTip(f"Tasks:\n{task_titles}")
                
                box_lay.addStretch()
                grid.addWidget(day_box, row, col)
                current_date += timedelta(days=1)

        self.container_scroll.setWidget(calendar_widget)

    def open_quick_add_task(self):
        if self.mainWindow:
            self.mainWindow.open_quick_add(tabIndex=0)
            
    def update_accent(self, color):
        self.accent_color = color
        self.btn_new_task.setStyleSheet(f"background-color: {color}; color: #0B0B0C; font-size: 11px; padding: 4px 10px;")
        self.refresh_view()
