import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt

class HexViewerWidget(QWidget):
    """Widget for displaying bit streams as hex dumps and searching for sync words."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Hex Sync Word (e.g. 1A 3F)")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)
        
        # Text view
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)
        
        layout.addWidget(self.text_edit)
        
        self.current_bits = None
        self.hex_lines = []
        
    def update_bits(self, bits: np.ndarray):
        """Update the viewer with a new bit array."""
        from src.core.bitstream import bits_to_hex_lines
        self.current_bits = bits
        self.hex_lines = bits_to_hex_lines(bits, bytes_per_line=16)
        
        self.text_edit.clear()
        self.text_edit.setPlainText('\n'.join(self.hex_lines))
        
    def _perform_search(self):
        """Highlight search terms in the hex dump."""
        query = self.search_input.text().strip().replace(' ', '').upper()
        if not query or len(query) % 2 != 0:
            return
            
        # Very basic text highlighting (for a production app, we'd do proper bit correlation)
        # Reset format
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setBackground(Qt.GlobalColor.transparent)
        cursor.setCharFormat(fmt)
        
        # Highlight matches
        fmt.setBackground(QColor('#e94560'))
        
        # Add spaces between bytes to match display format
        formatted_query = ' '.join(query[i:i+2] for i in range(0, len(query), 2))
        
        doc = self.text_edit.document()
        highlight_cursor = QTextCursor(doc)
        
        while not highlight_cursor.isNull() and not highlight_cursor.atEnd():
            highlight_cursor = doc.find(formatted_query, highlight_cursor)
            if not highlight_cursor.isNull():
                highlight_cursor.setCharFormat(fmt)
