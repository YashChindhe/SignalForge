from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QSpinBox, QPushButton, QFormLayout, QStackedWidget

class DeinterleaveControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        group = QGroupBox("De-Interleaving")
        vbox = QVBoxLayout()
        
        # Method selection
        form_top = QFormLayout()
        self.combo_method = QComboBox()
        self.combo_method.addItems(["Block", "Convolutional", "Diagonal", "Pseudo-Random"])
        form_top.addRow("Method:", self.combo_method)
        vbox.addLayout(form_top)
        
        # Stacked widget for parameters
        self.stack = QStackedWidget()
        
        # 1. Block params
        w_block = QWidget()
        f_block = QFormLayout(w_block)
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 10000)
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 10000)
        f_block.addRow("Rows:", self.spin_rows)
        f_block.addRow("Cols:", self.spin_cols)
        self.stack.addWidget(w_block)
        
        # 2. Convolutional params
        w_conv = QWidget()
        f_conv = QFormLayout(w_conv)
        self.spin_branches = QSpinBox()
        self.spin_branches.setRange(1, 1000)
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(1, 1000)
        f_conv.addRow("Branches (B):", self.spin_branches)
        f_conv.addRow("Delay (M):", self.spin_delay)
        self.stack.addWidget(w_conv)
        
        # 3. Diagonal params (stub)
        w_diag = QWidget()
        self.stack.addWidget(w_diag)
        
        # 4. PR params (stub)
        w_pr = QWidget()
        self.stack.addWidget(w_pr)
        
        vbox.addWidget(self.stack)
        
        self.combo_method.currentIndexChanged.connect(self.stack.setCurrentIndex)
        
        self.btn_apply = QPushButton("🔄 Apply De-Interleaving")
        vbox.addWidget(self.btn_apply)
        
        group.setLayout(vbox)
        layout.addWidget(group)
        layout.addStretch()
        
    def get_params(self):
        method = self.combo_method.currentText().lower()
        if method == "block":
            return {"method": "block", "rows": self.spin_rows.value(), "cols": self.spin_cols.value()}
        elif method == "convolutional":
            return {"method": "convolutional", "num_branches": self.spin_branches.value(), "delay": self.spin_delay.value()}
        return {"method": method}
