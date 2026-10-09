from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout
from src.core.file_ingest import IQFormat

class FileLoaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Load Button
        self.btn_load = QPushButton("📂 Load Signal File (.wav / .iq)")
        self.btn_load.setStyleSheet("font-size: 14px; padding: 12px; background-color: #0f3460;")
        layout.addWidget(self.btn_load)
        
        # IQ Options (Hidden by default, shown if .iq is selected in main window)
        self.iq_panel = QWidget()
        iq_layout = QVBoxLayout(self.iq_panel)
        iq_layout.setContentsMargins(0, 5, 0, 0)
        
        lbl = QLabel("Raw IQ Format Options:")
        lbl.setStyleSheet("color: #e94560;")
        iq_layout.addWidget(lbl)
        
        self.combo_format = QComboBox()
        for fmt in IQFormat:
            self.combo_format.addItem(fmt.name, fmt)
        iq_layout.addWidget(self.combo_format)
        
        # Note: In a real app we'd add sample rate input here for raw IQ
        # For this skeleton, we'll assume a default or use the spinbox in demod controls
        
        layout.addWidget(self.iq_panel)
        self.iq_panel.hide()
        
    def show_iq_options(self, show=True):
        self.iq_panel.setVisible(show)
        
    def get_iq_format(self):
        return self.combo_format.currentData()
