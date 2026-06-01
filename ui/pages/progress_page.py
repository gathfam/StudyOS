import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

import core.services.TaskService as TaskService
import core.services.FocusService as FocusService
import core.services.DeadlineService as DeadlineService
from core.events import eventBus
from modules.planner.controller import PlannerController

class CircularGauge(QWidget):
    """Custom premium circular progress gauge (Monochrome with single accent color)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(130, 130)
        self.percent = 0.0
        self.accent_color = "#BCA7FF"

    def setPercent(self, percent):
        self.percent = percent
        self.update()

    def setAccentColor(self, color):
        self.accent_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        size = min(w, h) - 20
        if size <= 0:
            return
            
        x = (w - size) / 2
        y = (h - size) / 2
        
        # Track Circle (Obisidan dark border)
        painter.setPen(QPen(QColor("#252529"), 6, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(x, y, size, size)
        
        # Progress Arc (start at top: 90 degrees)
        start_angle = 90 * 16
        span_angle = -int((self.percent / 100.0) * 360 * 16)
        
        painter.setPen(QPen(QColor(self.accent_color), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(x, y, size, size, start_angle, span_angle)
        
        # Inner text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 15, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(x, y, size, size, Qt.AlignmentFlag.AlignCenter, f"{int(self.percent)}%")


class AnalyticsBarChart(QWidget):
    """Custom bar chart showing general study performance (Monochrome with single accent)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)
        self.data = [0] * 7
        self.labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.accent_color = "#BCA7FF"

    def setData(self, data):
        self.data = data
        self.update()

    def setAccentColor(self, color):
        self.accent_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        left_m, right_m = 25, 10
        top_m, bottom_m = 15, 25
        chart_w = w - left_m - right_m
        chart_h = h - top_m - bottom_m
        
        if chart_w <= 0 or chart_h <= 0:
            return
            
        # Draw background grid lines (Minimal borders)
        painter.setPen(QPen(QColor("#252529"), 1, Qt.PenStyle.SolidLine))
        max_val = max(self.data) if self.data and max(self.data) > 0 else 5
        grid_lines = 4
        
        for i in range(grid_lines + 1):
            y = top_m + chart_h - (i * (chart_h / grid_lines))
            painter.drawLine(left_m, y, w - right_m, y)
            val = int(i * (max_val / grid_lines))
            painter.setPen(QColor("#8B8B92"))
            painter.drawText(5, y + 4, str(val))
            painter.setPen(QPen(QColor("#252529"), 1, Qt.PenStyle.SolidLine))

        # Draw bars
        bar_count = len(self.data)
        spacing = chart_w / bar_count
        bar_w = spacing * 0.4
        
        for i, val in enumerate(self.data):
            x = left_m + (i * spacing) + (spacing - bar_w) / 2
            ratio = val / max_val if max_val > 0 else 0
            bar_h = chart_h * ratio
            y = top_m + chart_h - bar_h
            
            painter.setBrush(QBrush(QColor(self.accent_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 2, 2)
            
            painter.setPen(QColor("#8B8B92"))
            painter.drawText(x + (bar_w - 20)/2, h - 8, self.labels[i])


class ProgressPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.plannerController = PlannerController(taskService=TaskService, eventBus=eventBus)
        
        # Subscribe
        eventBus.subscribe("taskCreated", self.refresh_analytics)
        eventBus.subscribe("taskDeleted", self.refresh_analytics)
        eventBus.subscribe("taskCompleted", self.refresh_analytics)
        eventBus.subscribe("focusSessionSaved", self.refresh_analytics)
        
        self.init_ui()
        self.refresh_analytics()

    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("mainContentSurface")
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet("QWidget#scrollContent { background: transparent; }")
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title
        title_widget = QWidget()
        v_title = QVBoxLayout(title_widget)
        v_title.setContentsMargins(0, 0, 0, 0)
        v_title.setSpacing(2)
        self.title_lbl = QLabel("Progress & Analytics")
        self.title_lbl.setObjectName("appTitle")
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        subtitle = QLabel("Academic analytics metrics and weekly summary")
        subtitle.setObjectName("appSubtitle")
        subtitle.setStyleSheet("color: #8B8B92; font-size: 11px;")
        v_title.addWidget(self.title_lbl)
        v_title.addWidget(subtitle)
        layout.addWidget(title_widget)

        # 4 Stats Cards Grid
        grid_cards = QGridLayout()
        grid_cards.setSpacing(12)
        layout.addLayout(grid_cards)

        self.cards = []
        card_configs = [
            ("Total Tasks", "0"),
            ("Completed Tasks", "0"),
            ("Active Projects", "0"),
            ("Study Hours", "0.0")
        ]

        for i, (title, default_val) in enumerate(card_configs):
            card = QFrame()
            card.setObjectName("rightPanel")
            card.setStyleSheet("#rightPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(15, 15, 15, 15)
            card_lay.setSpacing(5)
            
            val_lbl = QLabel(default_val)
            val_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #F2F2F2;")
            
            title_lbl = QLabel(title.upper())
            title_lbl.setStyleSheet("color: #8B8B92; font-size: 9px; font-weight: bold; letter-spacing: 0.5px;")
            
            card_lay.addWidget(val_lbl)
            card_lay.addWidget(title_lbl)
            
            row = i // 2
            col = i % 2
            grid_cards.addWidget(card, row, col)
            self.cards.append(val_lbl)

        # Performance Split charts layout
        h_split = QHBoxLayout()
        h_split.setSpacing(15)
        layout.addLayout(h_split)

        # Bar chart container
        chart_card = QFrame()
        chart_card.setObjectName("leftPanel")
        chart_card.setStyleSheet("#leftPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
        chart_card_lay = QVBoxLayout(chart_card)
        chart_card_lay.setContentsMargins(15, 15, 15, 15)
        
        lbl_bar = QLabel("WEEKLY PRODUCTIVITY")
        lbl_bar.setStyleSheet("font-size: 9px; font-weight: bold; color: #8B8B92; letter-spacing: 0.8px; margin-bottom: 5px;")
        chart_card_lay.addWidget(lbl_bar)
        
        self.bar_chart = AnalyticsBarChart()
        chart_card_lay.addWidget(self.bar_chart)
        h_split.addWidget(chart_card, 2)

        # Circular Gauge Container
        gauge_card = QFrame()
        gauge_card.setObjectName("rightPanel")
        gauge_card.setStyleSheet("#rightPanel { background-color: #141416; border: 1px solid #252529; border-radius: 4px; }")
        gauge_card_lay = QVBoxLayout(gauge_card)
        gauge_card_lay.setContentsMargins(15, 15, 15, 15)
        gauge_card_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_gauge = QLabel("COMPLETION RATE")
        lbl_gauge.setStyleSheet("font-size: 9px; font-weight: bold; color: #8B8B92; letter-spacing: 0.8px; margin-bottom: 5px;")
        gauge_card_lay.addWidget(lbl_gauge)
        
        self.gauge = CircularGauge()
        gauge_card_lay.addWidget(self.gauge)
        
        desc_lbl = QLabel("Percent of academic tasks resolved")
        desc_lbl.setStyleSheet("color: #8B8B92; font-size: 10px; margin-top: 5px;")
        gauge_card_lay.addWidget(desc_lbl)
        h_split.addWidget(gauge_card, 1)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def refresh_analytics(self, *args, **kwargs):
        tasks = self.plannerController.loadTasks() or []
        history = FocusService.getFocusHistory() or []
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("completed") == 1])
        
        subjects = set(t["subject"] for t in tasks if t.get("subject"))
        active_projects = len(subjects)
        
        completed_sessions = [s for s in history if s.get("completed") == 1]
        study_hours = sum(s.get("duration", 0) for s in completed_sessions) / 60.0
        
        self.cards[0].setText(str(total_tasks))
        self.cards[1].setText(str(completed_tasks))
        self.cards[2].setText(str(active_projects))
        self.cards[3].setText(f"{study_hours:.1f}")

        # Draw Weekly completions
        week_completions = [0] * 7
        for t in tasks:
            if t.get("completed") == 1:
                updated_at = t.get("updatedAt", "")
                try:
                    if updated_at:
                        dt = datetime.strptime(updated_at.split(" ")[0], "%Y-%m-%d")
                        day_idx = dt.weekday()
                        week_completions[day_idx] += 1
                except:
                    week_completions[2] += 1
        self.bar_chart.setData(week_completions)

        rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 100.0
        self.gauge.setPercent(rate)

    def update_accent(self, color):
        self.gauge.setAccentColor(color)
        self.bar_chart.setAccentColor(color)
