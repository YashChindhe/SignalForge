from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QSpinBox, QPushButton, QFormLayout, QStackedWidget

class FECControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        group = QGroupBox("Forward Error Correction (FEC)")
        vbox = QVBoxLayout()
        
        form_top = QFormLayout()
        self.combo_method = QComboBox()
        self.combo_method.addItems(["Viterbi (Convolutional)", "Reed-Solomon", "LDPC", "Concatenated"])
        form_top.addRow("Decoder:", self.combo_method)
        vbox.addLayout(form_top)
        
        self.stack = QStackedWidget()
        
        # 1. Viterbi params
        w_vit = QWidget()
        f_vit = QFormLayout(w_vit)
        self.spin_k = QSpinBox()
        self.spin_k.setRange(3, 9)
        self.spin_k.setValue(7)
        self.spin_rate = QComboBox()
        self.spin_rate.addItems(["1/2", "1/3"])
        f_vit.addRow("Constraint Len (K):", self.spin_k)
        f_vit.addRow("Code Rate:", self.spin_rate)
        self.stack.addWidget(w_vit)
        
        # 2. RS params
        w_rs = QWidget()
        f_rs = QFormLayout(w_rs)
        self.spin_rs_n = QSpinBox()
        self.spin_rs_n.setRange(1, 1024)
        self.spin_rs_n.setValue(255)
        self.spin_rs_k = QSpinBox()
        self.spin_rs_k.setRange(1, 1024)
        self.spin_rs_k.setValue(223)
        f_rs.addRow("Block Length (n):", self.spin_rs_n)
        f_rs.addRow("Msg Length (k):", self.spin_rs_k)
        self.stack.addWidget(w_rs)
        
        vbox.addWidget(self.stack)
        self.combo_method.currentIndexChanged.connect(self.stack.setCurrentIndex)
        
        self.btn_decode = QPushButton("Run FEC Decoder")
        vbox.addWidget(self.btn_decode)
        
        group.setLayout(vbox)
        layout.addWidget(group)
        layout.addStretch()
        
    def get_params(self):
        idx = self.combo_method.currentIndex()
        if idx == 0:
            rate_inv = 2 if self.spin_rate.currentText() == "1/2" else 3
            return {"method": "viterbi", "constraint_length": self.spin_k.value(), "code_rate_inv": rate_inv}
        elif idx == 1:
            return {"method": "reed_solomon", "n": self.spin_rs_n.value(), "k": self.spin_rs_k.value(), "nsym": self.spin_rs_n.value() - self.spin_rs_k.value()}
        elif idx == 2:
            return {"method": "ldpc"}
        elif idx == 3:
            return {"method": "concatenated"}
        return {"method": "unknown"}
