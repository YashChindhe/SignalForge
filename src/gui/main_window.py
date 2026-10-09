import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings

class SignalForgeWindow(QMainWindow):
    """SignalForge GUI presenting code.html via QWebEngineView."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SignalForge — RF Signal Intelligence Workbench")
        self.resize(1440, 900)
        
        # Central Web Engine View
        self.web_view = QWebEngineView()
        
        # Configure settings for smooth HTML5 rendering
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        # Load code.html (search in root, then CommonDocumentation/)
        html_path = self._resolve_html_path()
        if os.path.exists(html_path):
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath(html_path)))
        else:
            QMessageBox.critical(self, "File Not Found", f"Could not find UI layout file at:\n{html_path}")
            
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)
        self.setCentralWidget(central_widget)

    def _resolve_html_path(self) -> str:
        candidates = [
            os.path.join(os.getcwd(), "code.html"),
            os.path.join(os.getcwd(), "CommonDocumentation", "code.html"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SignalForge")
    app.setOrganizationName("Team Ramanuja")
    
    window = SignalForgeWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
