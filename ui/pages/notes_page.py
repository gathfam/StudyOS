import re
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QTextBrowser, QListWidget, QListWidgetItem,
    QSplitter, QFrame, QStackedWidget, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QFont

import core.services.NoteService as NoteService
from core.events import eventBus
from modules.notes.controller import NotesController
from modules.notes.handlers import NotesHandlers

class NotesPage(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.controller = NotesController(noteService=NoteService, eventBus=eventBus)
        self.handlers = NotesHandlers(controller=self.controller)
        
        # Subscribe
        eventBus.subscribe("noteCreated", self.refresh_note_list)
        eventBus.subscribe("noteUpdated", self.refresh_note_list)
        eventBus.subscribe("noteDeleted", self.refresh_note_list)
        
        self.active_note = None
        self.init_ui()
        self.refresh_note_list()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ==========================================
        # LEFT: NOTE EXPLORER (VS Code sidebar style)
        # ==========================================
        explorer_panel = QFrame()
        explorer_panel.setObjectName("leftPanel")
        explorer_lay = QVBoxLayout(explorer_panel)
        explorer_lay.setContentsMargins(10, 10, 10, 10)
        explorer_lay.setSpacing(8)

        lbl_title = QLabel("EXPLORER")
        lbl_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #8B8B92; letter-spacing: 0.8px;")
        explorer_lay.addWidget(lbl_title)
        
        self.btn_new_note = QPushButton("New Note")
        self.btn_new_note.setObjectName("btnPrimaryAccent")
        self.btn_new_note.setStyleSheet("QPushButton { font-size: 11px; padding: 4px 10px; }")
        self.btn_new_note.clicked.connect(self.create_new_blank_note)
        explorer_lay.addWidget(self.btn_new_note)

        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 4px;
                margin-bottom: 2px;
                color: #8B8B92;
                font-size: 11px;
            }
            QListWidget::item:hover {
                background-color: #1A1A1D;
                color: #F2F2F2;
            }
            QListWidget::item:selected {
                background-color: #1A1A1D;
                color: #BCA7FF;
                font-weight: 600;
            }
        """)
        self.notes_list.itemClicked.connect(self.on_note_selected)
        explorer_lay.addWidget(self.notes_list)
        
        splitter.addWidget(explorer_panel)

        # ==========================================
        # MIDDLE: EDITOR & PREVIEW (Obsidian Style)
        # ==========================================
        editor_panel = QFrame()
        editor_panel.setObjectName("mainContentSurface")
        editor_panel.setStyleSheet("#mainContentSurface { background-color: #141416; }")
        editor_lay = QVBoxLayout(editor_panel)
        editor_lay.setContentsMargins(15, 15, 15, 15)
        editor_lay.setSpacing(10)

        # Header Row
        h_title_row = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Untitled Note...")
        self.title_input.setStyleSheet("font-size: 15px; font-weight: bold; padding: 4px; background-color: #141416; border: none; border-bottom: 1px solid #252529; color: #ffffff;")
        self.title_input.textChanged.connect(self.on_note_content_changed)
        h_title_row.addWidget(self.title_input, 1)

        self.btn_toggle_edit = QPushButton("Edit")
        self.btn_toggle_edit.setObjectName("btnSecondary")
        self.btn_toggle_edit.setCheckable(True)
        self.btn_toggle_edit.setChecked(True)
        self.btn_toggle_edit.setStyleSheet("QPushButton { font-size: 10px; padding: 3px 8px; }")
        self.btn_toggle_edit.clicked.connect(self.toggle_editor_mode)
        
        self.btn_toggle_preview = QPushButton("Preview")
        self.btn_toggle_preview.setObjectName("btnSecondary")
        self.btn_toggle_preview.setCheckable(True)
        self.btn_toggle_preview.setStyleSheet("QPushButton { font-size: 10px; padding: 3px 8px; }")
        self.btn_toggle_preview.clicked.connect(self.toggle_editor_mode)
        
        h_title_row.addWidget(self.btn_toggle_edit)
        h_title_row.addWidget(self.btn_toggle_preview)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.setStyleSheet("QPushButton { font-size: 10px; padding: 3px 8px; }")
        self.btn_delete.clicked.connect(self.delete_current_note)
        h_title_row.addWidget(self.btn_delete)
        
        editor_lay.addLayout(h_title_row)

        self.editor_stack = QStackedWidget()
        
        # Editor
        self.note_edit_box = QTextEdit()
        self.note_edit_box.setStyleSheet("QTextEdit { background-color: #141416; border: none; color: #F2F2F2; font-family: monospace; font-size: 12px; }")
        self.note_edit_box.setPlaceholderText("Write notes in markdown...\n\nExample wikilinks: Type [[Note Title]] to link notes together.")
        self.note_edit_box.textChanged.connect(self.on_note_content_changed)
        self.editor_stack.addWidget(self.note_edit_box)
        
        # Preview
        self.note_preview_box = QTextBrowser()
        self.note_preview_box.setStyleSheet("QTextBrowser { background-color: #141416; border: none; color: #F2F2F2; }")
        self.note_preview_box.setOpenLinks(False)
        self.note_preview_box.anchorClicked.connect(self.on_wikilink_clicked)
        self.editor_stack.addWidget(self.note_preview_box)
        
        editor_lay.addWidget(self.editor_stack)
        splitter.addWidget(editor_panel)

        # ==========================================
        # RIGHT: META & BACKLINKS
        # ==========================================
        meta_panel = QFrame()
        meta_panel.setObjectName("rightPanel")
        meta_lay = QVBoxLayout(meta_panel)
        meta_lay.setContentsMargins(10, 10, 10, 10)
        meta_lay.setSpacing(15)

        # Outgoing
        lbl_out = QLabel("OUTGOING LINKS")
        lbl_out.setStyleSheet("font-size: 10px; font-weight: bold; color: #8B8B92; letter-spacing: 0.8px;")
        meta_lay.addWidget(lbl_out)
        
        self.outgoing_list = QListWidget()
        self.outgoing_list.setStyleSheet("""
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 4px;
                color: #8B8B92;
                font-size: 11px;
            }
            QListWidget::item:hover { color: #BCA7FF; }
        """)
        self.outgoing_list.itemClicked.connect(self.on_meta_link_clicked)
        meta_lay.addWidget(self.outgoing_list)

        # Backlinks
        lbl_back = QLabel("BACKLINKS")
        lbl_back.setStyleSheet("font-size: 10px; font-weight: bold; color: #8B8B92; letter-spacing: 0.8px;")
        meta_lay.addWidget(lbl_back)
        
        self.backlinks_list = QListWidget()
        self.backlinks_list.setStyleSheet("""
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 4px;
                color: #8B8B92;
                font-size: 11px;
            }
            QListWidget::item:hover { color: #BCA7FF; }
        """)
        self.backlinks_list.itemClicked.connect(self.on_meta_link_clicked)
        meta_lay.addWidget(self.backlinks_list)

        splitter.addWidget(meta_panel)
        splitter.setSizes([180, 640, 180])

    def refresh_note_list(self, *args, **kwargs):
        self.notes_list.clear()
        notes = self.controller.loadNotes() or []
        for note in notes:
            item = QListWidgetItem(note['title'])
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)
            
        if self.active_note:
            self.update_links_and_backlinks(notes)

    def on_note_selected(self, item):
        note = item.data(Qt.ItemDataRole.UserRole)
        self.load_note_by_id(note["id"])

    def load_note_by_id(self, note_id):
        self.active_note = None
        notes = self.controller.loadNotes() or []
        note = next((n for n in notes if n["id"] == note_id), None)
        if note:
            self.active_note = note
            self.title_input.setText(note["title"])
            self.note_edit_box.setPlainText(note.get("content") or "")
            self.update_links_and_backlinks(notes)
            self.render_markdown_preview()

    def load_note_by_title(self, title):
        notes = self.controller.loadNotes() or []
        note = next((n for n in notes if n["title"].lower() == title.lower()), None)
        if note:
            self.load_note_by_id(note["id"])
        else:
            reply = QMessageBox.question(
                self, "New Note",
                f"Note '{title}' does not exist. Do you want to create it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                new_note = NoteService.createNote(title, content=f"# {title}\n\nCreated from WikiLink.")
                if new_note:
                    self.refresh_note_list()
                    self.load_note_by_id(new_note["id"])

    def create_new_blank_note(self):
        new_note = NoteService.createNote("Untitled", content="# Untitled\n\nType note content...")
        if new_note:
            self.refresh_note_list()
            self.load_note_by_id(new_note["id"])

    def delete_current_note(self):
        if not self.active_note:
            return
        
        reply = QMessageBox.question(
            self, "Delete Note",
            f"Are you sure you want to delete '{self.active_note['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            NoteService.deleteNote(self.active_note["id"])
            self.active_note = None
            self.title_input.clear()
            self.note_edit_box.clear()
            self.refresh_note_list()

    def on_note_content_changed(self):
        if not self.active_note:
            return
        
        title = self.title_input.text().strip()
        content = self.note_edit_box.toPlainText()
        
        if not title:
            return
            
        try:
            NoteService.updateNote(self.active_note["id"], title=title, content=content)
            self.active_note["title"] = title
            self.active_note["content"] = content
        except Exception as e:
            print(f"Error auto-saving note: {e}")

    def toggle_editor_mode(self):
        if self.sender() == self.btn_toggle_edit:
            self.btn_toggle_preview.setChecked(False)
            self.editor_stack.setCurrentIndex(0)
        else:
            self.btn_toggle_edit.setChecked(False)
            self.editor_stack.setCurrentIndex(1)
            self.render_markdown_preview()

    def render_markdown_preview(self):
        if not self.active_note:
            self.note_preview_box.clear()
            return
            
        content = self.note_edit_box.toPlainText()
        html = content
        html = html.replace("<", "&lt;").replace(">", "&gt;")
        
        html = re.sub(r'^# (.*?)$', r'<h1 style="color: #ffffff; font-size: 16px;">\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2 style="color: #F2F2F2; font-size: 14px;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3 style="color: #8B8B92; font-size: 12px;">\1</h3>', html, flags=re.MULTILINE)
        
        html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
        
        def make_wikilink(match):
            name = match.group(1).strip()
            url_friendly = name.replace(" ", "_")
            return f'<a href="wiki://{url_friendly}" style="color: #BCA7FF; font-weight: bold; text-decoration: none;">[[{name}]]</a>'
            
        html = re.sub(r'\[\[(.*?)\]\]', make_wikilink, html)
        html = html.replace("\n", "<br>")
        
        styled_html = f"""
        <body style="font-family: sans-serif; color: #F2F2F2; font-size: 12px; line-height: 1.5; background-color: #141416;">
            {html}
        </body>
        """
        self.note_preview_box.setHtml(styled_html)

    def on_wikilink_clicked(self, url):
        if url.scheme() == "wiki":
            note_title = url.host().replace("_", " ")
            self.load_note_by_title(note_title)

    def update_links_and_backlinks(self, all_notes):
        self.outgoing_list.clear()
        self.backlinks_list.clear()
        
        if not self.active_note:
            return
            
        content = self.active_note.get("content") or ""
        outgoing = re.findall(r'\[\[(.*?)\]\]', content)
        for link in set(outgoing):
            title = link.strip()
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, title)
            self.outgoing_list.addItem(item)
            
        curr_title = self.active_note["title"].lower()
        for note in all_notes:
            if note["id"] == self.active_note["id"]:
                continue
            body = note.get("content") or ""
            links = re.findall(r'\[\[(.*?)\]\]', body)
            if any(l.strip().lower() == curr_title for l in links):
                item = QListWidgetItem(note['title'])
                item.setData(Qt.ItemDataRole.UserRole, note["title"])
                self.backlinks_list.addItem(item)

    def on_meta_link_clicked(self, item):
        note_title = item.data(Qt.ItemDataRole.UserRole)
        if note_title:
            self.load_note_by_title(note_title)
            
    def update_accent(self, color):
        self.btn_new_note.setStyleSheet(f"background-color: {color}; color: #0B0B0C;")
