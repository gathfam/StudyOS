import sys
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QDate

class QuickAddDialog(QDialog):
    """Clean, emojiless minimalist Quick Add modal (Linear/Obsidian-inspired)."""
    def __init__(self, parent=None, plannerHandlers=None, notesHandlers=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Add")
        self.resize(450, 380)
        self.setModal(True)
        
        self.plannerHandlers = plannerHandlers
        self.notesHandlers = notesHandlers
        
        self.init_ui()
        self.apply_style()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # ==========================================
        # TAB 1: ADD TASK
        # ==========================================
        self.task_tab = QWidget()
        task_layout = QVBoxLayout(self.task_tab)
        task_layout.setContentsMargins(10, 10, 10, 10)
        task_layout.setSpacing(8)

        task_layout.addWidget(QLabel("Task Name"))
        self.task_title = QLineEdit()
        self.task_title.setPlaceholderText("Title...")
        task_layout.addWidget(self.task_title)

        task_layout.addWidget(QLabel("Subject (Optional)"))
        self.task_subject = QLineEdit()
        self.task_subject.setPlaceholderText("e.g. Mathematics, Programming...")
        task_layout.addWidget(self.task_subject)

        task_layout.addWidget(QLabel("Description (Optional)"))
        self.task_desc = QLineEdit()
        self.task_desc.setPlaceholderText("Details...")
        task_layout.addWidget(self.task_desc)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)
        
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Due Date"))
        self.task_date = QDateEdit()
        self.task_date.setDate(QDate.currentDate().addDays(7))
        self.task_date.setCalendarPopup(True)
        self.task_date.setStyleSheet("QDateEdit { font-size: 11px; padding: 4px 8px; }")
        v1.addWidget(self.task_date)
        row_layout.addLayout(v1)

        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Priority"))
        self.task_priority = QComboBox()
        self.task_priority.addItems(["LOW", "MEDIUM", "HIGH"])
        self.task_priority.setCurrentIndex(1)
        self.task_priority.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        v2.addWidget(self.task_priority)
        row_layout.addLayout(v2)

        task_layout.addLayout(row_layout)
        
        self.task_submit_btn = QPushButton("Create Task")
        self.task_submit_btn.setObjectName("btnPrimaryAccent")
        self.task_submit_btn.clicked.connect(self.submit_task)
        task_layout.addWidget(self.task_submit_btn)
        task_layout.addStretch()

        self.tab_widget.addTab(self.task_tab, "Task")

        # ==========================================
        # TAB 2: ADD NOTE
        # ==========================================
        self.note_tab = QWidget()
        note_layout = QVBoxLayout(self.note_tab)
        note_layout.setContentsMargins(10, 10, 10, 10)
        note_layout.setSpacing(8)

        note_layout.addWidget(QLabel("Note Name"))
        self.note_title = QLineEdit()
        self.note_title.setPlaceholderText("Title...")
        note_layout.addWidget(self.note_title)

        note_layout.addWidget(QLabel("Category"))
        self.note_type = QComboBox()
        self.note_type.addItems(["QUICK", "KULIAH", "PERSONAL", "TUGAS"])
        self.note_type.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        note_layout.addWidget(self.note_type)

        note_layout.addWidget(QLabel("Content"))
        self.note_content = QTextEdit()
        self.note_content.setPlaceholderText("Write content...")
        note_layout.addWidget(self.note_content)

        self.note_submit_btn = QPushButton("Create Note")
        self.note_submit_btn.setObjectName("btnPrimaryAccent")
        self.note_submit_btn.clicked.connect(self.submit_note)
        note_layout.addWidget(self.note_submit_btn)
        note_layout.addStretch()

        self.tab_widget.addTab(self.note_tab, "Note")

    def apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0B0B0C;
            }
            QTabWidget::pane {
                border: 1px solid #252529;
                background-color: #141416;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #1A1A1D;
                color: #8B8B92;
                padding: 6px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #252529;
                margin-right: 2px;
                font-size: 11px;
            }
            QTabBar::tab:hover {
                background-color: #252529;
                color: #F2F2F2;
            }
            QTabBar::tab:selected {
                background-color: #141416;
                color: #BCA7FF;
                border-bottom: 1px solid #141416;
                font-weight: bold;
            }
        """)

    def submit_task(self):
        title = self.task_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Failed", "Task title cannot be empty.")
            return
            
        subject = self.task_subject.text().strip() or None
        desc = self.task_desc.text().strip() or None
        due_date_str = self.task_date.date().toString("yyyy-MM-dd")
        priority = self.task_priority.currentText()

        if self.plannerHandlers:
            self.plannerHandlers.handleAddTaskSubmit(
                title=title,
                subject=subject,
                description=desc,
                dueDate=due_date_str,
                plannedDate=QDate.currentDate().toString("yyyy-MM-dd"),
                priority=priority
            )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Planner Handler not configured.")

    def submit_note(self):
        title = self.note_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Failed", "Note title cannot be empty.")
            return
            
        note_type = self.note_type.currentText()
        content = self.note_content.toPlainText().strip() or None

        if self.notesHandlers:
            self.notesHandlers.handleAddNoteSubmit(
                title=title,
                content=content,
                noteType=note_type
            )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Notes Handler not configured.")
            
    def setTab(self, index):
        self.tab_widget.setCurrentIndex(index)
