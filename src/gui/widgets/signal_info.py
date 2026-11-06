from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QGroupBox

class SignalInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        group = QGroupBox("Signal Information")
        form = QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(10, 15, 10, 10)
        
        self.lbl_filename = QLabel("-")
        self.lbl_format = QLabel("-")
        self.lbl_samples = QLabel("-")
        self.lbl_sample_rate = QLabel("-")
        self.lbl_duration = QLabel("-")
        self.lbl_bw = QLabel("-")
        
        form.addRow("File:", self.lbl_filename)
        form.addRow("Format:", self.lbl_format)
        form.addRow("Samples:", self.lbl_samples)
        form.addRow("Sample Rate:", self.lbl_sample_rate)
        form.addRow("Duration:", self.lbl_duration)
        form.addRow("Est. Bandwidth:", self.lbl_bw)
        
        group.setLayout(form)
        layout.addWidget(group)
        # Removed layout.addStretch() to prevent squishing
        
    def update_info(self, signal_data, spectral_data=None):
        self.lbl_filename.setText(signal_data.filename.split('/')[-1].split('\\')[-1])
        self.lbl_format.setText(signal_data.source_format.upper())
        self.lbl_samples.setText(f"{signal_data.num_samples:,}")
        self.lbl_sample_rate.setText(f"{signal_data.sample_rate / 1000.0:.1f} kHz")
        self.lbl_duration.setText(f"{signal_data.duration:.3f} s")
        
        if spectral_data:
            self.lbl_bw.setText(f"{spectral_data.bandwidth_3db / 1000.0:.1f} kHz (-3dB)")
