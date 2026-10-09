from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QDoubleSpinBox, QPushButton, QFormLayout

class DemodControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        group = QGroupBox("Demodulation Parameters")
        form = QFormLayout()
        
        self.spin_symbol_rate = QDoubleSpinBox()
        self.spin_symbol_rate.setRange(0, 10000000)
        self.spin_symbol_rate.setDecimals(1)
        self.spin_symbol_rate.setSpecialValueText("Auto-detect")
        self.spin_symbol_rate.setValue(0)
        self.spin_symbol_rate.setSuffix(" sym/s")
        
        form.addRow("Symbol Rate:", self.spin_symbol_rate)
        
        self.btn_demodulate = QPushButton("📻 Run Demodulation")
        form.addRow(self.btn_demodulate)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        
    def get_symbol_rate(self):
        val = self.spin_symbol_rate.value()
        return val if val > 0 else None
