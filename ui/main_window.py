import os
import sys
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QStackedWidget, QDialog,
    QFrame, QGraphicsDropShadowEffect, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PySide6.QtGui import QFont, QKeySequence, QColor, QShortcut

# Imports pages
from ui.pages.dashboard_page import DashboardPage
from ui.pages.planner_page import PlannerPage
from ui.pages.deadlines_page import DeadlinesPage
from ui.pages.notes_page import NotesPage
from ui.pages.pomodoro_page import PomodoroPage
from ui.pages.progress_page import ProgressPage
from ui.pages.settings_page import SettingsPage

# Widgets & Themes
from ui.widgets.quick_add_dialog import QuickAddDialog
from ui.themes import getStylesheet
from core.events import eventBus
from core.utils.workspace_manager import getSettingsFilePath, loadSampleProject


class ToastNotification(QFrame):
    """Custom slide-in minimalist toast notification overlay (VS Code style)."""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setFixedHeight(45)
        self.setObjectName("toastFrame")
        self.setStyleSheet("""
            #toastFrame {
                background-color: #1A1A1D;
                border: 1px solid #BCA7FF;
                border-radius: 4px;
            }
            QLabel {
                color: #F2F2F2;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 5, 10, 5)
        self.lbl = QLabel(text)
        self.lbl.setWordWrap(True)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.lbl)
        
        self.show()
        
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.fade_out)
        self.close_timer.start(2500)

    def fade_out(self):
        self.close_timer.stop()
        self.deleteLater()


class CommandPaletteDialog(QDialog):
    """Fuzzy-search command palette modal dialog (Linear/Raycast style)."""
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(550, 300)
        
        self.callback = callback
        self.commands = [
            ("Create Task", "Tambahkan tugas baru secara cepat", "TASK"),
            ("Create Note", "Buat catatan baru", "NOTE"),
            ("Start Pomodoro", "Mulai atau jeda timer fokus", "POMO"),
            ("Go to Planner", "Navigasi ke Kanban board utama", "GOTO_PLANNER"),
            ("Go to Deadlines", "Tinjau linimasa tenggat waktu", "GOTO_DEADLINES"),
            ("Go to Settings", "Konfigurasi tampilan dan manajemen workspace", "GOTO_SETTINGS"),
            ("Search Notes", "Fokus pencarian dokumen catatan", "SEARCH_NOTES")
        ]
        
        self.init_ui()

    def init_ui(self):
        outer_frame = QFrame(self)
        outer_frame.setObjectName("paletteFrame")
        outer_frame.setStyleSheet("""
            #paletteFrame {
                background-color: #141416;
                border: 1px solid #252529;
                border-radius: 6px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 4)
        outer_frame.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(outer_frame)
        
        lay = QVBoxLayout(outer_frame)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        
        # Search Box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search actions...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1A1A1D;
                border: 1px solid #252529;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                color: #F2F2F2;
            }
            QLineEdit:focus {
                border: 1px solid #BCA7FF;
            }
        """)
        self.search_input.textChanged.connect(self.filter_commands)
        self.search_input.installEventFilter(self)
        lay.addWidget(self.search_input)
        
        # List of options
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border-radius: 4px;
                padding: 6px 10px;
                color: #8B8B92;
                font-size: 12px;
            }
            QListWidget::item:hover {
                background-color: #1A1A1D;
                color: #F2F2F2;
            }
            QListWidget::item:selected {
                background-color: #1A1A1D;
                border-left: 2px solid #BCA7FF;
                color: #F2F2F2;
            }
        """)
        self.list_widget.itemClicked.connect(self.command_triggered)
        lay.addWidget(self.list_widget)
        
        self.populate_commands()

    def populate_commands(self):
        self.list_widget.clear()
        for label, desc, cmd_type in self.commands:
            item = QListWidgetItem(f"{label} \t— {desc}")
            item.setData(Qt.ItemDataRole.UserRole, cmd_type)
            self.list_widget.addItem(item)
        self.list_widget.setCurrentRow(0)

    def filter_commands(self, text):
        query = text.lower().strip()
        self.list_widget.clear()
        
        for label, desc, cmd_type in self.commands:
            if query in label.lower() or query in desc.lower():
                item = QListWidgetItem(f"{label} \t— {desc}")
                item.setData(Qt.ItemDataRole.UserRole, cmd_type)
                self.list_widget.addItem(item)
                
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def eventFilter(self, obj, event):
        if obj == self.search_input and event.type() == event.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Down:
                row = self.list_widget.currentRow()
                self.list_widget.setCurrentRow((row + 1) % self.list_widget.count())
                return True
            elif key == Qt.Key.Key_Up:
                row = self.list_widget.currentRow()
                self.list_widget.setCurrentRow((row - 1 + self.list_widget.count()) % self.list_widget.count())
                return True
            elif key == Qt.Key.Key_Return:
                self.command_triggered(self.list_widget.currentItem())
                return True
            elif key == Qt.Key.Key_Escape:
                self.reject()
                return True
        return super().eventFilter(obj, event)

    def command_triggered(self, item):
        if not item:
            return
        cmd_type = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        if self.callback:
            self.callback(cmd_type)


class FirstLaunchWizard(QDialog):
    """Clean, typography-first wizard overlay."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setObjectName("wizardDialog")
        self.setStyleSheet("""
            #wizardDialog {
                background-color: #141416;
                border: 1px solid #252529;
                border-radius: 6px;
            }
            QLabel {
                color: #F2F2F2;
            }
            QPushButton {
                background-color: #BCA7FF;
                color: #0B0B0C;
                font-weight: 600;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d1c4ff;
            }
            QPushButton#btnSecondary {
                background-color: #1A1A1D;
                color: #8B8B92;
                border: 1px solid #252529;
            }
            QPushButton#btnSecondary:hover {
                background-color: #252529;
                color: #F2F2F2;
            }
        """)
        self.resize(450, 240)
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 25, 25, 25)
        lay.setSpacing(15)

        title = QLabel("StudyOS Setup")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        desc = QLabel("Pilih inisialisasi ruang kerja akademik Anda:")
        desc.setStyleSheet("color: #8B8B92; font-size: 12px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(desc)

        h_buttons = QHBoxLayout()
        h_buttons.setSpacing(12)

        self.btn_sample = QPushButton("Muat Proyek Sampel")
        self.btn_sample.clicked.connect(self.load_sample)
        
        self.btn_empty = QPushButton("Workspace Kosong")
        self.btn_empty.setObjectName("btnSecondary")
        self.btn_empty.clicked.connect(self.load_empty)

        h_buttons.addWidget(self.btn_sample, 1)
        h_buttons.addWidget(self.btn_empty, 1)
        
        lay.addLayout(h_buttons)

    def load_sample(self):
        loadSampleProject()
        self.accept()

    def load_empty(self):
        self.accept()


class ErrorBoundaryWidget(QWidget):
    """Clean recovery boundary interface."""
    def __init__(self, parent=None, exception_msg=""):
        super().__init__(parent)
        self.exception_msg = exception_msg
        self.setObjectName("errorBoundary")
        self.setStyleSheet("""
            #errorBoundary {
                background-color: #0B0B0C;
            }
            QLabel {
                color: #F2F2F2;
            }
            QPushButton {
                background-color: #1A1A1D;
                color: #E57373;
                border: 1px solid #E57373;
                border-radius: 4px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #E57373;
                color: #0B0B0C;
            }
            QPushButton#btnSecondary {
                background-color: #1A1A1D;
                color: #8B8B92;
                border: 1px solid #252529;
            }
            QPushButton#btnSecondary:hover {
                background-color: #252529;
                color: #F2F2F2;
            }
        """)
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(15)

        title = QLabel("Unable to Load Workspace")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E57373;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        desc = QLabel("StudyOS gagal mengakses database lokal. Berkas mungkin dikunci atau rusak.")
        desc.setStyleSheet("color: #8B8B92; font-size: 13px; max-width: 450px;")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(desc)

        if self.exception_msg:
            ex_box = QFrame()
            ex_box.setStyleSheet("background-color: #141416; border: 1px solid #252529; border-radius: 4px; padding: 10px;")
            ex_lay = QVBoxLayout(ex_box)
            ex_lbl = QLabel(f"Details:\n{self.exception_msg}")
            ex_lbl.setStyleSheet("font-family: monospace; font-size: 11px; color: #E57373;")
            ex_lbl.setWordWrap(True)
            ex_lay.addWidget(ex_lbl)
            lay.addWidget(ex_box)

        h_lay = QHBoxLayout()
        h_lay.setSpacing(12)
        
        self.btn_retry = QPushButton("Coba Lagi")
        self.btn_retry.clicked.connect(self.retry_launch)
        
        self.btn_logs = QPushButton("Buka Folder")
        self.btn_logs.setObjectName("btnSecondary")
        self.btn_logs.clicked.connect(self.open_logs)

        h_lay.addWidget(self.btn_retry)
        h_lay.addWidget(self.btn_logs)
        lay.addLayout(h_lay)

    def retry_launch(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def open_logs(self):
        db_dir = os.path.dirname(dbPath)
        QDesktopServices.openUrl(QUrl.fromLocalFile(db_dir))


class CustomTitleBar(QFrame):
    """Custom drag bar containing integrated desktop controls (Obsidian/VS Code hybrid)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("topBarContainer")
        self.setFixedHeight(35)
        self.drag_position = QPoint()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Title
        logo = QLabel("🌀")
        logo.setStyleSheet("font-size: 13px;")
        layout.addWidget(logo)
        
        self.title = QLabel("StudyOS")
        self.title.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 12px;")
        layout.addWidget(self.title)

        # Active Workspace Label
        self.workspace_lbl = QLabel("—  Academic")
        self.workspace_lbl.setStyleSheet("color: #8B8B92; font-size: 11px;")
        layout.addWidget(self.workspace_lbl)

        layout.addStretch()

        # Window Controls
        self.btn_min = QPushButton("—")
        self.btn_min.setFixedSize(22, 22)
        self.btn_min.setStyleSheet("QPushButton { border: none; background: transparent; color: #8B8B92; font-size: 10px; } QPushButton:hover { background-color: #252529; color: #ffffff; }")
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.btn_min)

        self.btn_max = QPushButton("⤢")
        self.btn_max.setFixedSize(22, 22)
        self.btn_max.setStyleSheet("QPushButton { border: none; background: transparent; color: #8B8B92; font-size: 9px; } QPushButton:hover { background-color: #252529; color: #ffffff; }")
        self.btn_max.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.btn_max)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setStyleSheet("QPushButton { border: none; background: transparent; color: #8B8B92; font-size: 10px; } QPushButton:hover { background-color: #E57373; color: #0B0B0C; }")
        self.btn_close.clicked.connect(self.parent_window.close)
        layout.addWidget(self.btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyOS")
        self.resize(1100, 700)
        
        # Frameless Window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Load app preferences
        self.settings = {}
        self.load_settings()
        
        # Init UI Structure
        self.init_ui()
        self.register_global_shortcuts()
        
        # Check for first launch wizard
        if self.settings.get("enableStartupWizard", True):
            QTimer.singleShot(100, self.launch_first_time_wizard)

    def load_settings(self):
        settings_path = getSettingsFilePath()
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading settings file: {e}")
                self.settings = {}
                
        # Default fallback values
        self.settings.setdefault("accentColor", "#BCA7FF")
        self.settings.setdefault("fontSize", 13)
        self.settings.setdefault("defaultStartupPage", "Dashboard")
        self.settings.setdefault("defaultSidebarState", "Expanded")
        self.settings.setdefault("enableStartupWizard", True)

    def save_settings(self):
        settings_path = getSettingsFilePath()
        try:
            with open(settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error writing settings: {e}")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Vertical Shell Layout: Title bar on top, body below
        shell_layout = QVBoxLayout(central_widget)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        # Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        shell_layout.addWidget(self.title_bar)

        # Body Layout: Sidebar + Main Section
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        shell_layout.addWidget(body_widget)

        # ==========================================
        # LEFT COLLAPSIBLE SIDEBAR
        # ==========================================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebarContainer")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(8, 10, 8, 10)
        self.sidebar_layout.setSpacing(4)

        # Navigation page links (Clean monochrome labels - NO EMOJIS)
        self.nav_buttons = []
        pages_config = [
            ("Dashboard", "Dashboard"),
            ("Planner", "Planner"),
            ("Deadlines", "Deadlines"),
            ("Notes", "Notes"),
            ("Pomodoro", "Pomodoro"),
            ("Progress", "Progress"),
            ("Settings", "Settings")
        ]
        
        for page_name, btn_text in pages_config:
            btn = QPushButton(btn_text)
            btn.setObjectName("sidebarBtn")
            btn.setCheckable(True)
            btn.clicked.connect(self.on_sidebar_click)
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons.append((page_name, btn))

        self.sidebar_layout.addStretch()

        # Collapse Button
        self.btn_collapse = QPushButton("Collapse")
        self.btn_collapse.setObjectName("btnSecondary")
        self.btn_collapse.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(self.btn_collapse)

        body_layout.addWidget(self.sidebar)

        # ==========================================
        # MAIN SECTION (TOPBAR + CONTENT)
        # ==========================================
        main_section = QWidget()
        v_main = QVBoxLayout(main_section)
        v_main.setContentsMargins(0, 0, 0, 0)
        v_main.setSpacing(0)

        # Minimal Top bar for search and actions
        top_action_bar = QFrame()
        top_action_bar.setObjectName("topBarContainer")
        top_action_bar_lay = QHBoxLayout(top_action_bar)
        top_action_bar_lay.setContentsMargins(15, 6, 15, 6)
        top_action_bar_lay.setSpacing(10)

        top_action_bar_lay.addStretch()

        # Global Search Bar (Minimalist)
        self.top_search = QLineEdit()
        self.top_search.setPlaceholderText("Search items... (Ctrl+F)")
        self.top_search.setFixedWidth(200)
        self.top_search.setStyleSheet("QLineEdit { background-color: #141416; border: 1px solid #252529; border-radius: 4px; padding: 4px 8px; font-size: 11px; }")
        self.top_search.textChanged.connect(self.on_global_search)
        top_action_bar_lay.addWidget(self.top_search)

        # Quick Add (+) Button
        self.btn_quick_add = QPushButton("+")
        self.btn_quick_add.setObjectName("btnPrimaryAccent")
        self.btn_quick_add.setFixedSize(26, 24)
        self.btn_quick_add.clicked.connect(self.open_quick_add)
        top_action_bar_lay.addWidget(self.btn_quick_add)

        v_main.addWidget(top_action_bar)

        # MAIN CONTENT STACK
        self.page_stack = QStackedWidget()
        v_main.addWidget(self.page_stack)

        body_layout.addWidget(main_section)

        # Instantiate Pages
        self.pages = {
            "Dashboard": DashboardPage(mainWindow=self),
            "Planner": PlannerPage(mainWindow=self),
            "Deadlines": DeadlinesPage(mainWindow=self),
            "Notes": NotesPage(mainWindow=self),
            "Pomodoro": PomodoroPage(mainWindow=self),
            "Progress": ProgressPage(mainWindow=self),
            "Settings": SettingsPage(mainWindow=self)
        }

        for page in self.pages.values():
            self.page_stack.addWidget(page)

        # Initial style sheet and startup page selection
        self.update_appearance(self.settings["accentColor"], self.settings["fontSize"])
        
        # Load startup page
        startup_page = self.settings["defaultStartupPage"]
        self.navigate_to(startup_page)

        # Set default sidebar state
        if self.settings.get("defaultSidebarState") == "Collapsed":
            self.toggle_sidebar(instant=True)

        # Floating Search Results list widget
        self.search_results = QListWidget(self)
        self.search_results.setStyleSheet("""
            QListWidget {
                background-color: #141416;
                border: 1px solid #252529;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 6px;
                color: #8B8B92;
                font-size: 11px;
            }
            QListWidget::item:hover {
                background-color: #1A1A1D;
                color: #F2F2F2;
            }
        """)
        self.search_results.setFixedWidth(200)
        self.search_results.setVisible(False)
        self.search_results.itemClicked.connect(self.on_search_result_clicked)

    def register_global_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+K"), self, self.open_command_palette)
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.open_quick_add(tabIndex=1))
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, lambda: self.open_quick_add(tabIndex=0))
        QShortcut(QKeySequence("Ctrl+P"), self, self.quick_toggle_pomodoro)
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_global_search)

    def navigate_to(self, page_name):
        page = self.pages.get(page_name)
        if page:
            idx = self.page_stack.indexOf(page)
            self.page_stack.setCurrentIndex(idx)
            for name, btn in self.nav_buttons:
                btn.setChecked(name == page_name)
            self.settings["lastActivePage"] = page_name
            self.save_settings()

    def get_page(self, page_name):
        return self.pages.get(page_name)

    def on_sidebar_click(self):
        sender = self.sender()
        for name, btn in self.nav_buttons:
            if btn == sender:
                self.navigate_to(name)
                break

    def toggle_sidebar(self, instant=False):
        is_collapsed = self.sidebar.width() < 80
        target_w = 160 if is_collapsed else 50
        
        self.settings["defaultSidebarState"] = "Collapsed" if not is_collapsed else "Expanded"
        self.save_settings()

        if is_collapsed:
            self.btn_collapse.setText("Collapse")
            for name, btn in self.nav_buttons:
                btn.setText(name)
        else:
            self.btn_collapse.setText(">")
            for name, btn in self.nav_buttons:
                # Use only first character for collapsed view
                btn.setText(name[0])

        if instant:
            self.sidebar.setFixedWidth(target_w)
            return

        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(120)
        self.anim.setStartValue(self.sidebar.width())
        self.anim.setEndValue(target_w)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim2.setDuration(120)
        self.anim2.setStartValue(self.sidebar.width())
        self.anim2.setEndValue(target_w)
        self.anim2.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.anim.start()
        self.anim2.start()

    def focus_global_search(self):
        self.top_search.setFocus()
        self.top_search.selectAll()

    def on_global_search(self, text):
        query = text.lower().strip()
        if not query:
            self.search_results.setVisible(False)
            return

        self.search_results.clear()
        
        # Search Tasks
        tasks = self.pages["Planner"].controller.loadTasks() or []
        for t in tasks:
            if query in t["title"].lower() or (t.get("subject") and query in t["subject"].lower()):
                item = QListWidgetItem(f"Task: {t['title']}")
                item.setData(Qt.ItemDataRole.UserRole, ("Planner", t["id"]))
                self.search_results.addItem(item)
                
        # Search Notes
        notes = self.pages["Notes"].controller.loadNotes() or []
        for n in notes:
            if query in n["title"].lower() or (n.get("content") and query in n["content"].lower()):
                item = QListWidgetItem(f"Note: {n['title']}")
                item.setData(Qt.ItemDataRole.UserRole, ("Notes", n["id"]))
                self.search_results.addItem(item)
                
        if self.search_results.count() > 0:
            pos = self.top_search.mapTo(self, QPoint(0, self.top_search.height()))
            self.search_results.move(pos)
            self.search_results.setFixedHeight(min(self.search_results.count() * 32, 160))
            self.search_results.setVisible(True)
            self.search_results.raise_()
        else:
            self.search_results.setVisible(False)

    def on_search_result_clicked(self, item):
        self.search_results.setVisible(False)
        self.top_search.clear()
        page_name, entity_id = item.data(Qt.ItemDataRole.UserRole)
        
        self.navigate_to(page_name)
        if page_name == "Notes":
            notes_page = self.get_page("Notes")
            if notes_page:
                notes_page.load_note_by_id(entity_id)

    def open_command_palette(self):
        palette = CommandPaletteDialog(self, callback=self.on_command_selected)
        palette.move(self.rect().center() - palette.rect().center())
        palette.exec()

    def on_command_selected(self, cmd_type):
        if cmd_type == "TASK":
            self.open_quick_add(0)
        elif cmd_type == "NOTE":
            self.open_quick_add(1)
        elif cmd_type == "POMO":
            self.quick_toggle_pomodoro()
        elif cmd_type == "GOTO_PLANNER":
            self.navigate_to("Planner")
        elif cmd_type == "GOTO_DEADLINES":
            self.navigate_to("Deadlines")
        elif cmd_type == "GOTO_SETTINGS":
            self.navigate_to("Settings")
        elif cmd_type == "SEARCH_NOTES":
            self.navigate_to("Notes")
            self.pages["Notes"].title_input.setFocus()

    def open_quick_add(self, tabIndex=0):
        planner_handlers = self.pages["Planner"].handlers
        notes_handlers = self.pages["Notes"].handlers
        
        dialog = QuickAddDialog(self, plannerHandlers=planner_handlers, notesHandlers=notes_handlers)
        dialog.setTab(tabIndex)
        dialog.exec()
        
        self.show_toast("Item successfully added.")

    def show_toast(self, text):
        toast = ToastNotification(text, self)
        toast.move(self.width() - toast.width() - 20, 50)

    def quick_toggle_pomodoro(self):
        pomo = self.pages["Pomodoro"]
        pomo.toggle_timer()
        status = "running" if pomo.is_running else "paused"
        self.show_toast(f"Pomodoro {status}")

    def update_appearance(self, accent_color, font_size):
        self.settings["accentColor"] = accent_color
        self.settings["fontSize"] = font_size
        self.save_settings()

        qss = getStylesheet(accentColor=accent_color, fontSize=font_size)
        self.setStyleSheet(qss)
        
        self.pages["Settings"].load_settings(self.settings)
        
        for page in self.pages.values():
            if hasattr(page, "update_accent"):
                page.update_accent(accent_color)
                
        self.btn_quick_add.setStyleSheet(f"background-color: {accent_color}; color: #0B0B0C;")

    def update_workspace_settings(self, start_page, sidebar_state, enable_wizard):
        self.settings["defaultStartupPage"] = start_page
        self.settings["defaultSidebarState"] = sidebar_state
        self.settings["enableStartupWizard"] = enable_wizard
        self.save_settings()

    def launch_first_time_wizard(self):
        tasks = self.pages["Planner"].controller.loadTasks() or []
        if not tasks:
            wizard = FirstLaunchWizard(self)
            wizard.exec()
            self.refresh_all_pages()
            self.settings["enableStartupWizard"] = False
            self.save_settings()
            self.pages["Settings"].load_settings(self.settings)

    def refresh_all_pages(self):
        for name, page in self.pages.items():
            if hasattr(page, "refresh_view"):
                page.refresh_view()
            elif hasattr(page, "refresh_dashboard"):
                page.refresh_dashboard()
            elif hasattr(page, "refresh_note_list"):
                page.refresh_note_list()
            elif hasattr(page, "refresh_tasks"):
                page.refresh_tasks()
                page.refresh_stats()
            elif hasattr(page, "refresh_analytics"):
                page.refresh_analytics()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.search_results.isVisible():
            pos = self.top_search.mapTo(self, QPoint(0, self.top_search.height()))
            self.search_results.move(pos)
