from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QComboBox, QProgressBar, QHBoxLayout

class ModulationPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        group = QGroupBox("AI Modulation Classification")
        vbox = QVBoxLayout()
        
        # Result layout
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Prediction:"))
        self.lbl_prediction = QLabel("None")
        self.lbl_prediction.setStyleSheet("font-weight: bold; color: #00ff88;")
        res_layout.addWidget(self.lbl_prediction)
        res_layout.addStretch()
        vbox.addLayout(res_layout)
        
        # Confidence
        self.progress_conf = QProgressBar()
        self.progress_conf.setRange(0, 100)
        self.progress_conf.setValue(0)
        self.progress_conf.setFormat("Confidence: %p%")
        vbox.addWidget(self.progress_conf)
        
        # Manual Override
        vbox.addWidget(QLabel("Manual Override (Force Type):"))
        self.combo_override = QComboBox()
        self.combo_override.addItems(["Auto (Use AI)", "BPSK", "QPSK", "8PSK", "2FSK", "4FSK", "16QAM"])
        vbox.addWidget(self.combo_override)
        
        group.setLayout(vbox)
        layout.addWidget(group)
        layout.addStretch()
        
    def update_result(self, classification_result):
        if classification_result is None:
            self.lbl_prediction.setText("Model Not Loaded")
            self.lbl_prediction.setStyleSheet("font-weight: bold; color: #ffaa00;")
            self.progress_conf.setValue(0)
            return
            
        self.lbl_prediction.setText(classification_result.predicted_mod)
        self.progress_conf.setValue(int(classification_result.confidence * 100))
        
    def get_selected_modulation(self):
        val = self.combo_override.currentText()
        if val == "Auto (Use AI)":
            return None
        return val
