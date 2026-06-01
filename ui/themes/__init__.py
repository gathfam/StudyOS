def getStylesheet(accentColor="#BCA7FF", fontSize=13):
    """
    Menghasilkan stylesheet QSS minimalis ala Obsidian & Linear.
    Background: #0B0B0C
    Surface: #141416
    Elevated Surface: #1A1A1D
    Border: #252529
    Accent: #BCA7FF
    Text Primary: #F2F2F2
    Text Secondary: #8B8B92
    """
    return f"""
    /* Global Styles */
    QMainWindow {{
        background-color: #0B0B0C;
    }}
    QWidget {{
        font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
        color: #F2F2F2;
        font-size: {fontSize}px;
    }}
    
    /* Surfaces */
    #leftPanel, #rightPanel, #mainContentSurface {{
        background-color: #141416;
        border-radius: 4px;
        border: 1px solid #252529;
    }}
    
    #sidebarContainer {{
        background-color: #0B0B0C;
        border-right: 1px solid #252529;
    }}
    
    #topBarContainer {{
        background-color: #0B0B0C;
        border-bottom: 1px solid #252529;
    }}
    
    /* Typography Helpers */
    .h1 {{
        font-size: {fontSize + 5}px;
        font-weight: 700;
        color: #F2F2F2;
        letter-spacing: -0.3px;
    }}
    .h2 {{
        font-size: {fontSize + 2}px;
        font-weight: 600;
        color: #F2F2F2;
    }}
    .dimText {{
        color: #8B8B92;
    }}
    
    /* Inputs & Form Controls */
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {{
        background-color: #141416;
        border: 1px solid #252529;
        border-radius: 4px;
        padding: 6px 10px;
        color: #F2F2F2;
        selection-background-color: {accentColor};
        selection-color: #0B0B0C;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
        border: 1px solid {accentColor};
    }}
    
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: #1A1A1D;
        color: #F2F2F2;
        border: 1px solid #252529;
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #252529;
        border-color: #3f3f46;
    }}
    QPushButton:pressed {{
        background-color: #141416;
    }}
    QPushButton:disabled {{
        background-color: #0B0B0C;
        color: #52525b;
        border-color: #18181b;
    }}
    
    /* Primary Accent Button */
    QPushButton#btnPrimaryAccent {{
        background-color: {accentColor};
        color: #0B0B0C;
        font-weight: 600;
        border: none;
    }}
    QPushButton#btnPrimaryAccent:hover {{
        background-color: #d1c4ff;
    }}
    
    /* Danger Button */
    QPushButton#btnDanger {{
        background-color: #1A1A1D;
        color: #E57373;
        border: 1px solid #E57373;
    }}
    QPushButton#btnDanger:hover {{
        background-color: #E57373;
        color: #0B0B0C;
    }}
    
    /* Sidebar Item Buttons */
    QPushButton#sidebarBtn {{
        background-color: transparent;
        color: #8B8B92;
        text-align: left;
        padding: 6px 10px;
        border-radius: 4px;
        border: none;
        font-weight: 400;
    }}
    QPushButton#sidebarBtn:hover {{
        background-color: #141416;
        color: #F2F2F2;
    }}
    QPushButton#sidebarBtn:checked {{
        background-color: #1A1A1D;
        color: {accentColor};
        font-weight: 600;
        border-left: 2px solid {accentColor};
        border-radius: 0px 4px 4px 0px;
    }}
    
    /* Lists and Tables */
    QListWidget, QTableWidget {{
        background-color: transparent;
        border: none;
        outline: none;
    }}
    QListWidget::item, QTableWidget::item {{
        background-color: #141416;
        border: 1px solid #252529;
        border-radius: 4px;
        margin-bottom: 6px;
        padding: 6px;
    }}
    QListWidget::item:hover, QTableWidget::item:hover {{
        background-color: #1A1A1D;
        border: 1px solid #313244;
    }}
    QListWidget::item:selected, QTableWidget::item:selected {{
        background-color: #1A1A1D;
        border: 1px solid {accentColor};
    }}
    
    /* Scrollbars (Linear minimalist style) */
    QScrollBar:vertical {{
        border: none;
        background: #0B0B0C;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #252529;
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #3f3f46;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    """
