import sys
import os

# Add root folder to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
import core

db_failed = False
ex_msg = ""

try:
    # 1. Startup the database schema and activity log listeners
    core.startup()
except Exception as e:
    # 2. Catch db failures for the error boundary recovery screen
    db_failed = True
    ex_msg = str(e)
    print(f"[Startup Error] Core failed to initialize: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if db_failed:
        # Load error recovery window
        from ui.main_window import ErrorBoundaryWidget
        window = ErrorBoundaryWidget(exception_msg=ex_msg)
        window.setWindowTitle("Error Boundary - StudyOS")
        window.resize(650, 420)
        window.show()
    else:
        # Load main application window
        from ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        
    sys.exit(app.exec())
