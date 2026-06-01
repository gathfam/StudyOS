import os
import shutil
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSpinBox, QCheckBox, QFileDialog, QMessageBox, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from core.database import dbPath
from core.utils.workspace_manager import exportWorkspace, importWorkspace, getSettingsFilePath

class SettingsPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.init_ui()

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
        layout.setSpacing(15)

        # Title
        title = QLabel("Settings")
        title.setObjectName("appTitle")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        subtitle = QLabel("Kustomisasi tampilan, alur kerja, dan manajemen berkas database StudyOS")
        subtitle.setStyleSheet("color: #8B8B92; font-size: 11px;")
        layout.addWidget(subtitle)

        # ==========================================
        # SECTION 1: APPEARANCE
        # ==========================================
        grp_appearance = QGroupBox("APPEARANCE")
        grp_appearance.setStyleSheet("QGroupBox { font-weight: bold; font-size: 9px; color: #8B8B92; border: 1px solid #252529; border-radius: 4px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        lay_appearance = QVBoxLayout(grp_appearance)
        lay_appearance.setSpacing(10)

        h_theme = QHBoxLayout()
        h_theme.addWidget(QLabel("Tema Aplikasi:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Mode (Obsidian-inspired)"])
        self.theme_combo.setEnabled(False)
        self.theme_combo.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        h_theme.addWidget(self.theme_combo)
        lay_appearance.addLayout(h_theme)

        h_accent = QHBoxLayout()
        h_accent.addWidget(QLabel("Warna Aksen:"))
        self.accent_combo = QComboBox()
        self.accent_combo.addItem("Blue-Violet", "#BCA7FF")
        self.accent_combo.addItem("Ocean Blue", "#89b4fa")
        self.accent_combo.addItem("Sage Green", "#a6e3a1")
        self.accent_combo.addItem("Amber Orange", "#fab387")
        self.accent_combo.addItem("Rose Red", "#f38ba8")
        self.accent_combo.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        self.accent_combo.currentIndexChanged.connect(self.save_appearance_settings)
        h_accent.addWidget(self.accent_combo)
        lay_appearance.addLayout(h_accent)

        h_font = QHBoxLayout()
        h_font.addWidget(QLabel("Ukuran Font UI:"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(11, 16)
        self.font_spin.setValue(13)
        self.font_spin.setStyleSheet("QSpinBox { font-size: 11px; padding: 4px 8px; }")
        self.font_spin.valueChanged.connect(self.save_appearance_settings)
        h_font.addWidget(self.font_spin)
        lay_appearance.addLayout(h_font)

        layout.addWidget(grp_appearance)

        # ==========================================
        # SECTION 2: WORKSPACE
        # ==========================================
        grp_workspace = QGroupBox("WORKSPACE")
        grp_workspace.setStyleSheet("QGroupBox { font-weight: bold; font-size: 9px; color: #8B8B92; border: 1px solid #252529; border-radius: 4px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        lay_workspace = QVBoxLayout(grp_workspace)
        lay_workspace.setSpacing(10)

        h_start = QHBoxLayout()
        h_start.addWidget(QLabel("Halaman Utama Startup:"))
        self.start_combo = QComboBox()
        self.start_combo.addItems(["Dashboard", "Planner", "Deadlines", "Notes", "Pomodoro", "Progress"])
        self.start_combo.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        self.start_combo.currentIndexChanged.connect(self.save_workspace_settings)
        h_start.addWidget(self.start_combo)
        lay_workspace.addLayout(h_start)

        h_sidebar = QHBoxLayout()
        h_sidebar.addWidget(QLabel("Default Tampilan Sidebar:"))
        self.sidebar_combo = QComboBox()
        self.sidebar_combo.addItems(["Expanded", "Collapsed"])
        self.sidebar_combo.setStyleSheet("QComboBox { font-size: 11px; padding: 4px 8px; }")
        self.sidebar_combo.currentIndexChanged.connect(self.save_workspace_settings)
        h_sidebar.addWidget(self.sidebar_combo)
        lay_workspace.addLayout(h_sidebar)

        self.wizard_chk = QCheckBox("Aktifkan Wizard Inisialisasi Pertama (First Launch Wizard)")
        self.wizard_chk.setChecked(True)
        self.wizard_chk.setStyleSheet("QCheckBox { font-size: 11px; }")
        self.wizard_chk.stateChanged.connect(self.save_workspace_settings)
        lay_workspace.addWidget(self.wizard_chk)

        layout.addWidget(grp_workspace)

        # ==========================================
        # SECTION 3: DATA MANAGEMENT
        # ==========================================
        grp_data = QGroupBox("DATA MANAGEMENT")
        grp_data.setStyleSheet("QGroupBox { font-weight: bold; font-size: 9px; color: #8B8B92; border: 1px solid #252529; border-radius: 4px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        lay_data = QVBoxLayout(grp_data)
        lay_data.setSpacing(8)

        # Flat button style
        btn_qss = "QPushButton { font-size: 11px; padding: 5px 12px; }"

        self.btn_open_folder = QPushButton("Buka Folder Workspace")
        self.btn_open_folder.setStyleSheet(btn_qss)
        self.btn_open_folder.clicked.connect(self.open_workspace_folder)
        lay_data.addWidget(self.btn_open_folder)

        self.btn_backup = QPushButton("Cadangkan (Backup) Database")
        self.btn_backup.setStyleSheet(btn_qss)
        self.btn_backup.clicked.connect(self.backup_database)
        lay_data.addWidget(self.btn_backup)

        self.btn_restore = QPushButton("Pulihkan (Restore) Database")
        self.btn_restore.setStyleSheet(btn_qss)
        self.btn_restore.clicked.connect(self.restore_database)
        lay_data.addWidget(self.btn_restore)

        self.btn_export = QPushButton("Ekspor Workspace (.studyos)")
        self.btn_export.setStyleSheet(btn_qss)
        self.btn_export.clicked.connect(self.export_current_workspace)
        lay_data.addWidget(self.btn_export)

        self.btn_import = QPushButton("Impor Workspace (.studyos)")
        self.btn_import.setStyleSheet(btn_qss)
        self.btn_import.clicked.connect(self.import_new_workspace)
        lay_data.addWidget(self.btn_import)

        layout.addWidget(grp_data)

        # ==========================================
        # SECTION 4: ABOUT
        # ==========================================
        grp_about = QGroupBox("ABOUT")
        grp_about.setStyleSheet("QGroupBox { font-weight: bold; font-size: 9px; color: #8B8B92; border: 1px solid #252529; border-radius: 4px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        lay_about = QVBoxLayout(grp_about)
        lay_about.setSpacing(6)

        lbl_app = QLabel("<b>Aplikasi:</b> StudyOS Productivity Workspace (v1.0.0)")
        lbl_app.setStyleSheet("color: #F2F2F2; font-size: 11px;")
        lay_about.addWidget(lbl_app)
        
        lbl_db = QLabel(f"<b>Database:</b> SQLite 3 (Database Path: {dbPath})")
        lbl_db.setStyleSheet("color: #F2F2F2; font-size: 11px;")
        lay_about.addWidget(lbl_db)
        
        lbl_qt = QLabel(f"<b>GUI Framework:</b> PySide6 (v{sys.modules['PySide6'].__version__})")
        lbl_qt.setStyleSheet("color: #F2F2F2; font-size: 11px;")
        lay_about.addWidget(lbl_qt)
        
        lbl_lic = QLabel("<b>Lisensi:</b> MIT License")
        lbl_lic.setStyleSheet("color: #F2F2F2; font-size: 11px;")
        lay_about.addWidget(lbl_lic)

        layout.addWidget(grp_about)
        layout.addStretch()

        scroll.setWidget(scroll_content)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def load_settings(self, settings):
        accent = settings.get("accentColor", "#BCA7FF")
        idx = self.accent_combo.findData(accent)
        if idx >= 0:
            self.accent_combo.setCurrentIndex(idx)
        else:
            self.accent_combo.setCurrentIndex(0)

        self.font_spin.setValue(settings.get("fontSize", 13))

        start_page = settings.get("defaultStartupPage", "Dashboard")
        idx_page = self.start_combo.findText(start_page)
        if idx_page >= 0:
            self.start_combo.setCurrentIndex(idx_page)

        sidebar_state = settings.get("defaultSidebarState", "Expanded")
        idx_side = self.sidebar_combo.findText(sidebar_state)
        if idx_side >= 0:
            self.sidebar_combo.setCurrentIndex(idx_side)

        self.wizard_chk.setChecked(settings.get("enableStartupWizard", True))

    def save_appearance_settings(self):
        if not self.mainWindow:
            return
        accent = self.accent_combo.currentData()
        font_size = self.font_spin.value()
        self.mainWindow.update_appearance(accent, font_size)

    def save_workspace_settings(self):
        if not self.mainWindow:
            return
        start_page = self.start_combo.currentText()
        sidebar_state = self.sidebar_combo.currentText()
        enable_wizard = self.wizard_chk.isChecked()
        self.mainWindow.update_workspace_settings(start_page, sidebar_state, enable_wizard)

    def open_workspace_folder(self):
        db_dir = os.path.dirname(dbPath)
        QDesktopServices.openUrl(QUrl.fromLocalFile(db_dir))

    def backup_database(self):
        target_path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database SQLite", "", "SQLite Database (*.db)"
        )
        if target_path:
            try:
                shutil.copy2(dbPath, target_path)
                QMessageBox.information(self, "Backup Berhasil", f"Database berhasil dicadangkan ke:\n{target_path}")
            except Exception as e:
                QMessageBox.critical(self, "Gagal Cadangkan", f"Terjadi kesalahan saat mencadangkan database:\n{e}")

    def restore_database(self):
        reply = QMessageBox.warning(
            self, "Konfirmasi Pemulihan", 
            "Pemulihan database akan menimpa seluruh data saat ini secara permanen. Apakah Anda yakin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        source_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Database Hasil Cadangan", "", "SQLite Database (*.db)"
        )
        if source_path:
            try:
                shutil.copy2(dbPath, dbPath + ".bak")
                shutil.copy2(source_path, dbPath)
                QMessageBox.information(self, "Pemulihan Berhasil", "Database berhasil dipulihkan! Memuat ulang data...")
                if self.mainWindow:
                    self.mainWindow.refresh_all_pages()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Pulihkan", f"Terjadi kesalahan saat memulihkan database:\n{e}")

    def export_current_workspace(self):
        target_path, _ = QFileDialog.getSaveFileName(
            self, "Ekspor Workspace StudyOS", "workspace.studyos", "StudyOS Archive (*.studyos *.zip)"
        )
        if target_path:
            success = exportWorkspace(target_path)
            if success:
                QMessageBox.information(self, "Ekspor Berhasil", f"Workspace berhasil diekspor ke:\n{target_path}")
            else:
                QMessageBox.critical(self, "Ekspor Gagal", "Terjadi kesalahan saat mengekspor workspace.")

    def import_new_workspace(self):
        source_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Berkas Workspace StudyOS", "", "StudyOS Archive (*.studyos *.zip)"
        )
        if not source_path:
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Metode Impor")
        msg_box.setText("Pilih metode untuk mengimpor workspace:")
        btn_replace = msg_box.addButton("Menimpa (REPLACE)", QMessageBox.ButtonRole.DestructiveRole)
        btn_merge = msg_box.addButton("Menggabungkan (MERGE)", QMessageBox.ButtonRole.AcceptRole)
        btn_cancel = msg_box.addButton(QMessageBox.StandardButton.Cancel)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_replace:
            mode = "REPLACE"
        elif msg_box.clickedButton() == btn_merge:
            mode = "MERGE"
        else:
            return

        success = importWorkspace(source_path, mode=mode)
        if success:
            QMessageBox.information(self, "Impor Berhasil", f"Workspace berhasil diimpor menggunakan metode {mode}!")
            if self.mainWindow:
                self.mainWindow.load_settings()
                self.mainWindow.refresh_all_pages()
        else:
            QMessageBox.critical(self, "Impor Gagal", "Gagal mengimpor berkas workspace.")
