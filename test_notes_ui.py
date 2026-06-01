import sys
import os

# Add the workspace root to Python path so core can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import core
from core.events import eventBus
import core.services.NoteService as NoteService
from modules.notes.controller import NotesController
from modules.notes.handlers import NotesHandlers

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

class NoteCard(QWidget):
    """Custom widget to represent a note as a modern card in the list."""
    def __init__(self, note):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title and Badge Layout
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        self.title_label = QLabel(note.get("title", ""))
        self.title_label.setObjectName("cardTitle")
        
        note_type = note.get("noteType", "QUICK").upper()
        self.type_badge = QLabel(note_type)
        self.type_badge.setObjectName("cardBadge")
        self.type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_badge.setMinimumWidth(70)
        
        # Color coding badges based on note type
        badge_colors = {
            "QUICK": "background-color: #89dceb; color: #11111b;",
            "KULIAH": "background-color: #cba6f7; color: #11111b;",
            "PERSONAL": "background-color: #a6e3a1; color: #11111b;",
            "TUGAS": "background-color: #f38ba8; color: #11111b;"
        }
        self.type_badge.setStyleSheet(badge_colors.get(note_type, "background-color: #89b4fa; color: #11111b;"))
        
        title_layout.addWidget(self.title_label, 1)
        title_layout.addWidget(self.type_badge)
        
        # Content snippet
        content_text = note.get("content", "")
        if len(content_text) > 100:
            content_text = content_text[:97] + "..."
        self.content_label = QLabel(content_text)
        self.content_label.setObjectName("cardContent")
        self.content_label.setWordWrap(True)
        
        # Date
        self.date_label = QLabel(f"Dibuat: {note.get('createdAt', '')}")
        self.date_label.setObjectName("cardDate")
        
        layout.addLayout(title_layout)
        layout.addWidget(self.content_label)
        layout.addWidget(self.date_label)


class NoteTesterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyOS - Note Services Architecture Tester")
        self.resize(1000, 680)
        
        # Initialize Core services and Module architecture
        core.startup()
        self.controller = NotesController(noteService=NoteService, eventBus=eventBus)
        self.handlers = NotesHandlers(controller=self.controller)
        
        # Subscribe to Event Bus to automatically refresh UI when data changes
        eventBus.subscribe("noteCreated", self.on_notes_changed)
        eventBus.subscribe("noteUpdated", self.on_notes_changed)
        eventBus.subscribe("noteDeleted", self.on_notes_changed)
        
        # State to keep track of active editing Note ID
        self.editing_note_id = None
        
        self.init_ui()
        self.apply_theme()
        self.refresh_notes_list()

    def init_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Splitter to separate Left Form Panel and Right List Panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ==========================================
        # LEFT PANEL: NOTE FORM
        # ==========================================
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        # Header Title
        self.form_header = QLabel("Buat Catatan Baru")
        self.form_header.setObjectName("appTitle")
        left_layout.addWidget(self.form_header)
        
        subtitle = QLabel("Uji fungsionalitas UI -> Modules -> Core Services")
        subtitle.setObjectName("appSubtitle")
        left_layout.addWidget(subtitle)

        # Input fields
        # Note ID (Read Only, only shown when editing)
        self.id_layout = QHBoxLayout()
        self.id_label_title = QLabel("Note ID:")
        self.id_label_val = QLabel("-")
        self.id_label_val.setStyleSheet("color: #fab387; font-weight: bold;")
        self.id_layout.addWidget(self.id_label_title)
        self.id_layout.addWidget(self.id_label_val)
        self.id_layout.addStretch()
        left_layout.addLayout(self.id_layout)

        # Title
        left_layout.addWidget(QLabel("Judul Catatan"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Masukkan judul catatan...")
        left_layout.addWidget(self.title_input)

        # Note Type
        left_layout.addWidget(QLabel("Tipe Catatan"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["QUICK", "KULIAH", "PERSONAL", "TUGAS"])
        left_layout.addWidget(self.type_combo)

        # Content
        left_layout.addWidget(QLabel("Konten / Isi Catatan"))
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Tulis isi catatan di sini...")
        left_layout.addWidget(self.content_input)

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Simpan Catatan")
        self.save_btn.clicked.connect(self.on_save_clicked)
        
        self.reset_btn = QPushButton("Batal / Reset")
        self.reset_btn.setObjectName("btnReset")
        self.reset_btn.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(self.save_btn, 2)
        btn_layout.addWidget(self.reset_btn, 1)
        left_layout.addLayout(btn_layout)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # ==========================================
        # RIGHT PANEL: NOTES LIST & ACTIONS
        # ==========================================
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # List Header
        list_header = QLabel("Daftar Catatan (Database)")
        list_header.setObjectName("appTitle")
        right_layout.addWidget(list_header)

        # Notes List Box
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(16, 16))
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        right_layout.addWidget(self.list_widget)

        # Status Label inside list if empty
        self.empty_label = QLabel("Belum ada catatan di database. Silakan buat di panel kiri!")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #7f849c; font-style: italic; font-size: 13px;")
        right_layout.addWidget(self.empty_label)

        # Actions Layout
        actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit Terpilih")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.on_edit_clicked)

        self.delete_btn = QPushButton("Hapus Catatan")
        self.delete_btn.setObjectName("btnDelete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.on_delete_clicked)

        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.delete_btn)
        right_layout.addLayout(actions_layout)

        splitter.addWidget(right_panel)
        
        # Set splitter proportions (40% form, 60% list)
        splitter.setSizes([400, 600])

    def apply_theme(self):
        """Styles the window with a gorgeous modern dark theme (based on Catppuccin Mocha colors)."""
        stylesheet = """
        /* Main Layout */
        QMainWindow {
            background-color: #0f0f11;
        }
        QWidget {
            font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
            color: #cdd6f4;
        }
        
        /* Panels */
        #leftPanel, #rightPanel {
            background-color: #151518;
            border-radius: 12px;
            border: 1px solid #27272a;
        }
        
        /* Headers */
        #appTitle {
            font-size: 20px;
            font-weight: bold;
            color: #cba6f7;
        }
        #appSubtitle {
            font-size: 12px;
            color: #a6adc8;
        }
        
        /* Form controls */
        QLabel {
            font-size: 13px;
            font-weight: bold;
            color: #bac2de;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #1e1e24;
            border: 1px solid #3f3f46;
            border-radius: 8px;
            padding: 10px;
            font-size: 13px;
            color: #ffffff;
            selection-background-color: #cba6f7;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 1px solid #cba6f7;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #cba6f7;
            color: #11111b;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #b4befe;
        }
        QPushButton:pressed {
            background-color: #89b4fa;
        }
        QPushButton:disabled {
            background-color: #313244;
            color: #585b70;
        }
        
        #btnDelete {
            background-color: #f38ba8;
            color: #11111b;
        }
        #btnDelete:hover {
            background-color: #f5c2e7;
        }
        #btnDelete:pressed {
            background-color: #eba0ac;
        }
        
        #btnReset {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
        }
        #btnReset:hover {
            background-color: #45475a;
        }
        #btnReset:pressed {
            background-color: #585b70;
        }
        
        /* Lists */
        QListWidget {
            background-color: transparent;
            border: none;
            outline: none;
        }
        QListWidget::item {
            background-color: #1e1e24;
            border: 1px solid #27272a;
            border-radius: 10px;
            margin-bottom: 10px;
            padding: 0px;
        }
        QListWidget::item:hover {
            background-color: #25252e;
            border: 1px solid #3f3f46;
        }
        QListWidget::item:selected {
            background-color: #2d2d3d;
            border: 1px solid #cba6f7;
        }
        
        /* Note Card Specifics */
        #cardTitle {
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
        }
        #cardContent {
            font-size: 12px;
            color: #a6adc8;
        }
        #cardDate {
            font-size: 10px;
            color: #7f849c;
        }
        #cardBadge {
            font-size: 10px;
            font-weight: bold;
            border-radius: 5px;
            padding: 3px 8px;
        }
        """
        self.setStyleSheet(stylesheet)

    # ==========================================
    # EVENT BUS CALLBACKS
    # ==========================================
    def on_notes_changed(self, *args, **kwargs):
        """Called automatically by EventBus when a note is created, updated, or deleted."""
        print(f"[EventBus Signal Received] Refreshing UI notes view...")
        self.refresh_notes_list()

    # ==========================================
    # LOGIC / ACTIONS
    # ==========================================
    def refresh_notes_list(self):
        """Loads notes from NotesController and populates the QListWidget."""
        self.list_widget.clear()
        
        # Load notes via the Controller -> NoteService -> Database
        notes = self.controller.loadNotes()
        
        if not notes:
            self.empty_label.setVisible(True)
            self.list_widget.setVisible(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
            
        self.empty_label.setVisible(False)
        self.list_widget.setVisible(True)
        
        for note in notes:
            item = QListWidgetItem()
            # Store the raw note dict in the list item
            item.setData(Qt.ItemDataRole.UserRole, note)
            
            card = NoteCard(note)
            item.setSizeHint(card.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)

    def on_selection_changed(self):
        """Updates delete/edit button enablement based on list selection."""
        selected_items = self.list_widget.selectedItems()
        has_selection = len(selected_items) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def on_save_clicked(self):
        """Collects form input and submits to the appropriate Handler action."""
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        note_type = self.type_combo.currentText()

        # Input validation
        if not title:
            QMessageBox.warning(self, "Validasi Gagal", "Judul catatan tidak boleh kosong!")
            return

        if self.editing_note_id is None:
            # CREATE NEW NOTE (via Handler)
            print(f"[UI] Adding note: '{title}'")
            self.handlers.handleAddNoteSubmit(title, content, note_type)
            QMessageBox.information(self, "Berhasil", f"Catatan '{title}' berhasil dibuat!")
        else:
            # UPDATE EXISTING NOTE (via Handler)
            print(f"[UI] Updating note ID {self.editing_note_id}: '{title}'")
            self.handlers.handleUpdateNoteSubmit(self.editing_note_id, title, content, note_type)
            QMessageBox.information(self, "Berhasil", f"Catatan '{title}' berhasil diperbaharui!")
        
        self.reset_form()

    def on_edit_clicked(self):
        """Loads the selected note into the form editor."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        note = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.editing_note_id = note.get("id")
        
        # Populate form
        self.id_label_val.setText(str(self.editing_note_id))
        self.title_input.setText(note.get("title", ""))
        self.content_input.setText(note.get("content", ""))
        
        # Match combo box index
        note_type = note.get("noteType", "QUICK")
        index = self.type_combo.findText(note_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
            
        # Update layout text
        self.form_header.setText("Edit Catatan")
        self.save_btn.setText("Simpan Perubahan")
        self.save_btn.setStyleSheet("background-color: #fab387; color: #11111b;") # Orange accent for editing

    def on_delete_clicked(self):
        """Triggers note deletion via Handler."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        note = selected_items[0].data(Qt.ItemDataRole.UserRole)
        note_id = note.get("id")
        note_title = note.get("title", "")
        
        reply = QMessageBox.question(
            self, 
            "Konfirmasi Hapus", 
            f"Apakah Anda yakin ingin menghapus catatan '{note_title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print(f"[UI] Deleting note ID {note_id}")
            self.handlers.handleDeleteNoteClick(note_id)
            QMessageBox.information(self, "Berhasil", "Catatan berhasil dihapus!")
            
            # If we deleted the note we were currently editing, reset the form
            if self.editing_note_id == note_id:
                self.reset_form()

    def reset_form(self):
        """Resets the form to add note mode."""
        self.editing_note_id = None
        self.id_label_val.setText("-")
        self.title_input.clear()
        self.content_input.clear()
        self.type_combo.setCurrentIndex(0)
        
        # Reset layout texts and button style
        self.form_header.setText("Buat Catatan Baru")
        self.save_btn.setText("Simpan Catatan")
        self.save_btn.setStyleSheet("") # Reverts back to main QSS style

        # Clear list selection
        self.list_widget.clearSelection()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteTesterWindow()
    window.show()
    sys.exit(app.exec())
