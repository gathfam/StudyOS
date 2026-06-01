import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, QTime

import core.services.FocusService as FocusService
import core.services.TaskService as TaskService
from core.events import eventBus
from modules.planner.controller import PlannerController

class PomodoroPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.plannerController = PlannerController(taskService=TaskService, eventBus=eventBus)
        
        self.work_duration = 25
        self.short_break = 5
        
        self.time_left_seconds = self.work_duration * 60
        self.is_running = False
        self.current_mode = "POMODORO"
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        
        self.accent_color = "#BCA7FF"
        self.init_ui()
        self.refresh_tasks()
        self.refresh_stats()
        
        eventBus.subscribe("taskCreated", self.refresh_tasks)
        eventBus.subscribe("taskDeleted", self.refresh_tasks)
        eventBus.subscribe("taskCompleted", self.refresh_tasks)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Row
        title_widget = QWidget()
        v_title = QVBoxLayout(title_widget)
        v_title.setContentsMargins(0, 0, 0, 0)
        v_title.setSpacing(2)
        self.title_lbl = QLabel("Focus Timer")
        self.title_lbl.setObjectName("appTitle")
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        subtitle = QLabel("Deep study block timer using the Pomodoro technique")
        subtitle.setObjectName("appSubtitle")
        subtitle.setStyleSheet("color: #8B8B92; font-size: 11px;")
        v_title.addWidget(self.title_lbl)
        v_title.addWidget(subtitle)
        layout.addWidget(title_widget)

        h_split = QHBoxLayout()
        layout.addLayout(h_split)

        # ==========================================
        # LEFT: TIMER FOCUS
        # ==========================================
        timer_panel = QFrame()
        timer_panel.setObjectName("leftPanel")
        timer_panel_lay = QVBoxLayout(timer_panel)
        timer_panel_lay.setContentsMargins(25, 25, 25, 25)
        timer_panel_lay.setSpacing(15)
        timer_panel_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mode Buttons (Flat, monochrome toggle)
        h_mode = QHBoxLayout()
        self.btn_pomo = QPushButton("Work Session")
        self.btn_pomo.setCheckable(True)
        self.btn_pomo.setChecked(True)
        self.btn_pomo.setStyleSheet("QPushButton:checked { background-color: #1A1A1D; border-color: #BCA7FF; color: #BCA7FF; }")
        self.btn_pomo.clicked.connect(self.set_pomodoro_mode)
        
        self.btn_break = QPushButton("Break Session")
        self.btn_break.setCheckable(True)
        self.btn_break.setStyleSheet("QPushButton:checked { background-color: #1A1A1D; border-color: #BCA7FF; color: #BCA7FF; }")
        self.btn_break.clicked.connect(self.set_break_mode)
        
        h_mode.addWidget(self.btn_pomo)
        h_mode.addWidget(self.btn_break)
        timer_panel_lay.addLayout(h_mode)

        # Task Selector
        self.task_selector = QComboBox()
        self.task_selector.setMinimumWidth(240)
        timer_panel_lay.addWidget(self.task_selector)

        # Clock Text (Large Mono text)
        self.time_lbl = QLabel("25:00")
        self.time_lbl.setStyleSheet("font-size: 72px; font-weight: bold; color: #ffffff; font-family: monospace;")
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_panel_lay.addWidget(self.time_lbl)

        # Controls Row
        h_ctrl = QHBoxLayout()
        self.btn_start = QPushButton("Start Focus")
        self.btn_start.setObjectName("btnPrimaryAccent")
        self.btn_start.setStyleSheet(f"QPushButton {{ background-color: {self.accent_color}; color: #0B0B0C; font-size: 13px; font-weight: bold; padding: 10px 24px; }}")
        self.btn_start.clicked.connect(self.toggle_timer)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setObjectName("btnSecondary")
        self.btn_reset.clicked.connect(self.reset_timer)
        self.btn_reset.setFixedWidth(75)
        
        h_ctrl.addWidget(self.btn_start)
        h_ctrl.addWidget(self.btn_reset)
        timer_panel_lay.addLayout(h_ctrl)

        h_split.addWidget(timer_panel, 2)

        # ==========================================
        # RIGHT: STATS (Dense & Emojiless)
        # ==========================================
        stats_panel = QFrame()
        stats_panel.setObjectName("rightPanel")
        stats_lay = QVBoxLayout(stats_panel)
        stats_lay.setContentsMargins(15, 15, 15, 15)
        stats_lay.setSpacing(12)

        lbl_stats = QLabel("STATS")
        lbl_stats.setStyleSheet("font-size: 10px; font-weight: bold; color: #8B8B92; letter-spacing: 0.8px;")
        stats_lay.addWidget(lbl_stats)

        grid_stats = QGridLayout()
        grid_stats.setSpacing(10)
        
        c1 = QFrame()
        c1.setStyleSheet("background-color: #1A1A1D; border: 1px solid #252529; border-radius: 4px; padding: 10px;")
        lay_c1 = QVBoxLayout(c1)
        self.lbl_pomo_count = QLabel("0")
        self.lbl_pomo_count.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.accent_color};")
        lay_c1.addWidget(self.lbl_pomo_count)
        lay_c1.addWidget(QLabel("Sessions"))
        grid_stats.addWidget(c1, 0, 0)

        c2 = QFrame()
        c2.setStyleSheet("background-color: #1A1A1D; border: 1px solid #252529; border-radius: 4px; padding: 10px;")
        lay_c2 = QVBoxLayout(c2)
        self.lbl_hours = QLabel("0.0")
        self.lbl_hours.setStyleSheet("font-size: 20px; font-weight: bold; color: #7FC97F;")
        lay_c2.addWidget(self.lbl_hours)
        lay_c2.addWidget(QLabel("Hours"))
        grid_stats.addWidget(c2, 0, 1)

        stats_lay.addLayout(grid_stats)
        stats_lay.addStretch()

        h_split.addWidget(stats_panel, 1)

    def refresh_tasks(self, *args, **kwargs):
        self.task_selector.clear()
        self.task_selector.addItem("Independent Study (No Task)")
        tasks = self.plannerController.loadTasks() or []
        pending = [t for t in tasks if t.get("completed") == 0]
        for t in pending:
            self.task_selector.addItem(t["title"], t["id"])

    def refresh_stats(self):
        history = FocusService.getFocusHistory() or []
        completed_sessions = [s for s in history if s.get("completed") == 1]
        pomodoros = [s for s in completed_sessions if s.get("sessionType") == "POMODORO"]
        
        total_duration_minutes = sum(s.get("duration", 0) for s in completed_sessions)
        hours = total_duration_minutes / 60.0
        
        self.lbl_pomo_count.setText(str(len(pomodoros)))
        self.lbl_hours.setText(f"{hours:.1f}")

    def set_pomodoro_mode(self):
        self.btn_pomo.setChecked(True)
        self.btn_break.setChecked(False)
        self.current_mode = "POMODORO"
        self.time_left_seconds = self.work_duration * 60
        self.update_timer_display()
        if self.is_running:
            self.toggle_timer()

    def set_break_mode(self):
        self.btn_pomo.setChecked(False)
        self.btn_break.setChecked(True)
        self.current_mode = "SHORT_BREAK"
        self.time_left_seconds = self.short_break * 60
        self.update_timer_display()
        if self.is_running:
            self.toggle_timer()

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.btn_start.setText("Resume")
            self.is_running = False
            eventBus.emit("pomodoroPaused")
        else:
            self.timer.start(1000)
            self.btn_start.setText("Pause")
            self.is_running = True
            eventBus.emit("pomodoroStarted")

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.btn_start.setText("Start Focus")
        
        if self.current_mode == "POMODORO":
            self.time_left_seconds = self.work_duration * 60
        else:
            self.time_left_seconds = self.short_break * 60
            
        self.update_timer_display()
        eventBus.emit("pomodoroReset")

    def on_timer_tick(self):
        if self.time_left_seconds > 0:
            self.time_left_seconds -= 1
            self.update_timer_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.btn_start.setText("Start Sesi")
            
            try:
                duration = self.work_duration if self.current_mode == "POMODORO" else self.short_break
                FocusService.saveFocusSession(
                    sessionType=self.current_mode,
                    duration=duration,
                    completed=1
                )
                QMessageBox.information(self, "Focus Complete", "Sesi fokus Pomodoro selesai.")
                self.refresh_stats()
            except Exception as e:
                print(f"Error saving completed session: {e}")

    def update_timer_display(self):
        minutes = self.time_left_seconds // 60
        seconds = self.time_left_seconds % 60
        self.time_lbl.setText(f"{minutes:02d}:{seconds:02d}")
        
    def update_accent(self, color):
        self.accent_color = color
        self.btn_start.setStyleSheet(f"QPushButton {{ background-color: {color}; color: #0B0B0C; font-size: 13px; font-weight: bold; padding: 10px 24px; }}")
        self.lbl_pomo_count.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
