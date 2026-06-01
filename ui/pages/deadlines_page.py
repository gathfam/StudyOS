import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

import core.services.TaskService as TaskService
import core.services.DeadlineService as DeadlineService
from core.events import eventBus
from modules.deadlines.controller import DeadlinesController
from modules.deadlines.handlers import DeadlinesHandlers
from modules.planner.controller import PlannerController

class DeadlineItemWidget(QFrame):
    """Custom flat widget to display deadline details, priority, and countdown (Obsidian style)."""
    def __init__(self, deadline, task, parent=None, deadlinesHandlers=None):
        super().__init__(parent)
        self.deadline = deadline
        self.task = task
        self.deadlinesHandlers = deadlinesHandlers
        self.setObjectName("deadlineCard")
        self.setStyleSheet("""
            #deadlineCard {
                background-color: #141416;
                border: 1px solid #252529;
                border-radius: 4px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Left Accent Border indicator instead of a color badge
        urgency = self.deadline.get("urgencyLevel", "MEDIUM")
        indicator = QFrame()
        indicator.setFixedWidth(3)
        indicator.setMinimumHeight(28)
        
        urgency_colors = {
            "HIGH": "#E57373",   # Red
            "MEDIUM": "#F2C66D", # Amber
            "LOW": "#7FC97F"     # Green
        }
        indicator.setStyleSheet(f"background-color: {urgency_colors.get(urgency, '#8B8B92')}; border-radius: 1px;")
        layout.addWidget(indicator)

        # Title & Meta Info (No emojis)
        details_lay = QVBoxLayout()
        details_lay.setSpacing(2)
        
        title_lbl = QLabel(self.task.get("title") if self.task else "Deadline Item")
        title_lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #ffffff;")
        details_lay.addWidget(title_lbl)
        
        meta_parts = []
        if self.task and self.task.get("subject"):
            meta_parts.append(self.task["subject"])
        if self.deadline.get("deadlineDate"):
            meta_parts.append(self.deadline["deadlineDate"])
        
        meta_lbl = QLabel(" | ".join(meta_parts))
        meta_lbl.setStyleSheet("color: #8B8B92; font-size: 11px;")
        details_lay.addWidget(meta_lbl)
        
        layout.addLayout(details_lay, 1)

        # Countdown Label
        countdown_lbl = QLabel()
        countdown_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        days_left = self.calculate_days_left()
        if days_left < 0:
            countdown_lbl.setText(f"{abs(days_left)} days overdue")
            countdown_lbl.setStyleSheet("color: #E57373; font-weight: bold; font-size: 11px;")
        elif days_left == 0:
            countdown_lbl.setText("due today")
            countdown_lbl.setStyleSheet("color: #F2C66D; font-weight: bold; font-size: 11px;")
        elif days_left == 1:
            countdown_lbl.setText("tomorrow")
            countdown_lbl.setStyleSheet("color: #F2C66D; font-weight: bold; font-size: 11px;")
        else:
            countdown_lbl.setText(f"{days_left} days left")
            countdown_lbl.setStyleSheet("color: #7FC97F; font-weight: bold; font-size: 11px;")

        layout.addWidget(countdown_lbl)

        # Minimal Action button
        self.btn_resolve = QPushButton("Resolve")
        self.btn_resolve.setFixedWidth(60)
        self.btn_resolve.setStyleSheet("QPushButton { font-size: 10px; padding: 3px 6px; }")
        self.btn_resolve.clicked.connect(self.resolve_deadline)
        layout.addWidget(self.btn_resolve)

    def calculate_days_left(self):
        due_str = self.deadline.get("deadlineDate")
        if not due_str:
            return 999
        try:
            due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            return (due_date - today).days
        except:
            return 999

    def resolve_deadline(self):
        if self.task and self.deadlinesHandlers:
            reply = QMessageBox.question(
                self, "Resolve Deadline",
                f"Mark task '{self.task['title']}' as completed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                TaskService.updateTaskStatus(self.task["id"], True)


class DeadlinesPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.controller = DeadlinesController(deadlineService=DeadlineService, eventBus=eventBus)
        self.handlers = DeadlinesHandlers(controller=self.controller)
        self.plannerController = PlannerController(taskService=TaskService, eventBus=eventBus)
        
        # Subscribe
        eventBus.subscribe("deadlineAdded", self.refresh_view)
        eventBus.subscribe("deadlineUpdated", self.refresh_view)
        eventBus.subscribe("deadlineDeleted", self.refresh_view)
        eventBus.subscribe("taskCompleted", self.refresh_view)
        eventBus.subscribe("taskUpdated", self.refresh_view)
        
        self.init_ui()
        self.refresh_view()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Row
        title_widget = QWidget()
        v_title = QVBoxLayout(title_widget)
        v_title.setContentsMargins(0, 0, 0, 0)
        v_title.setSpacing(2)
        self.title_lbl = QLabel("Deadlines")
        self.title_lbl.setObjectName("appTitle")
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        subtitle = QLabel("Chronological academic urgency tracker")
        subtitle.setObjectName("appSubtitle")
        subtitle.setStyleSheet("color: #8B8B92; font-size: 11px;")
        v_title.addWidget(self.title_lbl)
        v_title.addWidget(subtitle)
        layout.addWidget(title_widget)

        # Scroll Panel
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("mainContentSurface")
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        layout.addWidget(scroll)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet("QWidget#scrollContent { background: transparent; }")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(12)
        
        # Section Config
        self.categories = [
            ("Overdue", QListWidget(), QLabel("No overdue items.")),
            ("Due Today", QListWidget(), QLabel("No deadlines due today.")),
            ("Due This Week", QListWidget(), QLabel("No deadlines scheduled this week.")),
            ("Upcoming", QListWidget(), QLabel("No upcoming deadlines."))
        ]
        
        for cat_name, list_w, empty_lbl in self.categories:
            cat_frame = QFrame()
            cat_frame.setObjectName("rightPanel")
            cat_frame.setStyleSheet("#rightPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
            cat_frame_lay = QVBoxLayout(cat_frame)
            cat_frame_lay.setContentsMargins(12, 12, 12, 12)
            cat_frame_lay.setSpacing(8)
            
            lbl = QLabel(f"<b>{cat_name.upper()}</b>")
            lbl.setStyleSheet("font-size: 10px; color: #ffffff; font-weight: bold; letter-spacing: 0.5px;")
            cat_frame_lay.addWidget(lbl)
            
            list_w.setStyleSheet("""
                QListWidget { background: transparent; border: none; }
                QListWidget::item { background: transparent; border: none; padding: 0px; margin-bottom: 6px; }
            """)
            list_w.setMinimumHeight(45)
            cat_frame_lay.addWidget(list_w)
            
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #8B8B92; font-style: italic; font-size: 11px; padding: 10px 0;")
            cat_frame_lay.addWidget(empty_lbl)
            
            self.scroll_layout.addWidget(cat_frame)

        self.scroll_layout.addStretch()
        scroll.setWidget(scroll_content)

    def refresh_view(self, *args, **kwargs):
        deadlines = self.controller.loadDeadlines() or []
        tasks = self.plannerController.loadTasks() or []

        for _, list_w, _ in self.categories:
            list_w.clear()

        overdue_items = []
        today_items = []
        week_items = []
        upcoming_items = []
        
        today_date = datetime.now().date()

        for dl in deadlines:
            task = next((t for t in tasks if t["id"] == dl["taskId"]), None)
            if task and task.get("completed") == 1:
                continue

            due_str = dl.get("deadlineDate")
            if not due_str:
                continue
                
            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
                diff = (due_date - today_date).days
                
                if diff < 0:
                    overdue_items.append((dl, task))
                elif diff == 0:
                    today_items.append((dl, task))
                elif 0 < diff <= 7:
                    week_items.append((dl, task))
                else:
                    upcoming_items.append((dl, task))
            except Exception as e:
                print(f"Error parsing date {due_str}: {e}")
                upcoming_items.append((dl, task))

        self.render_category(self.categories[0], overdue_items)
        self.render_category(self.categories[1], today_items)
        self.render_category(self.categories[2], week_items)
        self.render_category(self.categories[3], upcoming_items)

    def render_category(self, cat_tuple, items):
        _, list_w, empty_lbl = cat_tuple
        if not items:
            list_w.setVisible(False)
            empty_lbl.setVisible(True)
        else:
            list_w.setVisible(True)
            empty_lbl.setVisible(False)
            
            for dl, task in items:
                item = QListWidgetItem()
                widget = DeadlineItemWidget(dl, task, deadlinesHandlers=self.handlers)
                item.setSizeHint(widget.sizeHint())
                list_w.addItem(item)
                list_w.setItemWidget(item, widget)
            
            # Adjust height dynamically
            list_w.setFixedHeight(len(items) * 52)
