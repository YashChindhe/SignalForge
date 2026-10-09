import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QTabWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QToolBar, QStatusBar, QFileDialog, QMessageBox, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from .widgets.file_loader import FileLoaderWidget
from .widgets.spectrum_plot import SpectrumPlotWidget
from .widgets.waterfall_plot import WaterfallPlotWidget
from .widgets.constellation import ConstellationWidget
from .widgets.signal_info import SignalInfoWidget
from .widgets.modulation_panel import ModulationPanelWidget
from .widgets.demod_controls import DemodControlsWidget
from .widgets.deinterleave_controls import DeinterleaveControlsWidget
from .widgets.fec_controls import FECControlsWidget
from .widgets.hex_viewer import HexViewerWidget

from .threads.worker import PipelineWorker
from src.core.pipeline import SignalForgePipeline

class MainWindow(QMainWindow):
    """SignalForge main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SignalForge — Automated Signal Analysis")
        self.setMinimumSize(1280, 800)
        
        # Initialize backend pipeline
        self.pipeline = SignalForgePipeline(
            model_path="models/rf_classifier.pkl",
            scaler_path="models/scaler.pkl",
            encoder_path="models/label_encoder.pkl"
        )
        
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._load_stylesheet()
        self._connect_signals()
    
    def _setup_ui(self):
        """Build the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # ── Left Panel: Controls ──
        left_panel = QVBoxLayout()
        
        self.file_loader = FileLoaderWidget()
        left_panel.addWidget(self.file_loader)
        
        self.signal_info = SignalInfoWidget()
        left_panel.addWidget(self.signal_info)
        
        self.mod_panel = ModulationPanelWidget()
        left_panel.addWidget(self.mod_panel)
        
        self.demod_controls = DemodControlsWidget()
        left_panel.addWidget(self.demod_controls)
        
        self.deinterleave_controls = DeinterleaveControlsWidget()
        left_panel.addWidget(self.deinterleave_controls)
        
        self.fec_controls = FECControlsWidget()
        left_panel.addWidget(self.fec_controls)
        
        left_panel.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(left_widget)
        scroll_area.setMaximumWidth(380)
        scroll_area.setMinimumWidth(300)
        
        # ── Right Panel: Visualization Tabs ──
        self.viz_tabs = QTabWidget()
        
        self.spectrum_plot = SpectrumPlotWidget()
        self.viz_tabs.addTab(self.spectrum_plot, "Spectrum / PSD")
        
        self.waterfall_plot = WaterfallPlotWidget()
        self.viz_tabs.addTab(self.waterfall_plot, "Waterfall")
        
        self.constellation = ConstellationWidget()
        self.viz_tabs.addTab(self.constellation, "Constellation")
        
        self.hex_viewer = HexViewerWidget()
        self.viz_tabs.addTab(self.hex_viewer, "Bit Stream")
        
        # ── Splitter ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(scroll_area)
        splitter.addWidget(self.viz_tabs)
        splitter.setSizes([350, 930])
        
        main_layout.addWidget(splitter)
    
    def _setup_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        self.action_load = QAction("Load File", self)
        self.action_analyze = QAction("Analyze", self)
        self.action_classify = QAction("Classify", self)
        self.action_demod = QAction("Demodulate", self)
        self.action_decode = QAction("Decode", self)
        self.action_theme = QAction("Toggle Theme", self)
        
        toolbar.addAction(self.action_load)
        toolbar.addAction(self.action_analyze)
        toolbar.addAction(self.action_classify)
        toolbar.addAction(self.action_demod)
        toolbar.addAction(self.action_decode)
        
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Preferred)
        toolbar.addWidget(spacer)
        toolbar.addAction(self.action_theme)
    
    def _setup_statusbar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready — Load a .wav or .IQ file to begin")
    
    def _load_stylesheet(self, theme_name="dark_theme.qss"):
        """Load QSS theme."""
        try:
            import os
            path = os.path.join("assets", "styles", theme_name)
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            # Clear stylesheet to revert to default if file not found
            self.setStyleSheet("")
    
    def _connect_signals(self):
        """Wire up UI signals to pipeline actions."""
        self.action_load.triggered.connect(self._on_load_file)
        self.action_analyze.triggered.connect(self._on_analyze_async)
        self.action_classify.triggered.connect(self._on_classify_async)
        self.action_demod.triggered.connect(self._on_demodulate_async)
        self.action_decode.triggered.connect(self._on_decode_async)
        self.action_theme.triggered.connect(self._toggle_theme)
        
        # Connect widget buttons
        self.file_loader.btn_load.clicked.connect(self._on_load_file)
        self.demod_controls.btn_demodulate.clicked.connect(self._on_demodulate_async)
        self.deinterleave_controls.btn_apply.clicked.connect(self._on_deinterleave_async)
        self.fec_controls.btn_decode.clicked.connect(self._on_decode_async)
        
        self._active_worker = None
        self._is_dark_mode = True
    
    # ── Slot implementations ──
    
    def _toggle_theme(self):
        """Toggle between light and dark mode."""
        self._is_dark_mode = not self._is_dark_mode
        if self._is_dark_mode:
            self._load_stylesheet("dark_theme.qss")
        else:
            self._load_stylesheet("light_theme.qss")
            
    def _on_load_file(self):
        """Handle file load."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Signal File", "",
            "Signal Files (*.wav *.iq *.raw *.bin);;All Files (*)"
        )
        if filepath:
            try:
                from src.core.file_ingest import IQFormat
                # If IQ, we'd ideally read from UI, hardcoding for now
                fmt = IQFormat.COMPLEX_FLOAT32 if filepath.endswith('.iq') else None
                sr = 100000.0 if filepath.endswith('.iq') else None
                
                signal = self.pipeline.stage1_load_file(filepath, iq_format=fmt, sample_rate=sr)
                self.signal_info.update_info(signal)
                self.file_loader.show_iq_options(filepath.endswith('.iq'))
                
                self.status_bar.showMessage(
                    f"Loaded: {signal.filename} — "
                    f"{signal.num_samples:,} samples @ "
                    f"{signal.sample_rate/1e3:.1f} kHz"
                )
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))
    
    def _on_analyze_async(self):
        """Run spectral analysis and classification asynchronously."""
        if self.pipeline.state.signal is None:
            return QMessageBox.warning(self, "Warning", "Please load a file first.")
            
        self.status_bar.showMessage("Analyzing...")
        self.viz_tabs.setCurrentIndex(0) # Go to spectrum tab
        
        self._active_worker = PipelineWorker(self.pipeline.stage2_analyze)
        self._active_worker.finished.connect(self._on_analyze_done)
        self._active_worker.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self._active_worker.start()
        
    def _on_analyze_done(self, result):
        spectral, classification = result
        self.spectrum_plot.update_plot(spectral)
        self.waterfall_plot.update_plot(spectral)
        self.mod_panel.update_result(classification)
        self.signal_info.update_info(self.pipeline.state.signal, spectral)
        
        # Auto-fill the manual override dropdown with the AI's prediction
        if classification and classification.predicted_mod:
            index = self.mod_panel.combo_override.findText(classification.predicted_mod)
            if index >= 0:
                self.mod_panel.combo_override.setCurrentIndex(index)
                
        self.status_bar.showMessage("Analysis complete")
    
    def _on_classify_async(self):
        self._on_analyze_async()
    
    def _on_demodulate_async(self):
        """Run demodulation asynchronously."""
        if self.pipeline.state.signal is None:
            return QMessageBox.warning(self, "Warning", "Please load a file first.")
            
        mod_override = self.mod_panel.get_selected_modulation()
        sym_rate = self.demod_controls.get_symbol_rate()
        
        self.status_bar.showMessage("Demodulating...")
        self.viz_tabs.setCurrentIndex(2) # Go to constellation tab
        
        self._active_worker = PipelineWorker(self.pipeline.stage3_demodulate, mod_type=mod_override, symbol_rate=sym_rate)
        self._active_worker.finished.connect(self._on_demodulate_done)
        self._active_worker.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self._active_worker.start()

    def _on_demodulate_done(self, result):
        self.constellation.update_plot(result)
        self.hex_viewer.update_bits(result.bits)
        self.status_bar.showMessage(
            f"Demodulated: {result.num_symbols} symbols -> "
            f"{len(result.bits)} bits"
        )
        
    def _on_deinterleave_async(self):
        if self.pipeline.state.demod is None:
            return QMessageBox.warning(self, "Warning", "Please run demodulation first.")
            
        params = self.deinterleave_controls.get_params()
        method = params.pop("method")
        
        self.status_bar.showMessage("De-interleaving...")
        self._active_worker = PipelineWorker(self.pipeline.stage4_deinterleave, method, **params)
        self._active_worker.finished.connect(self._on_deinterleave_done)
        self._active_worker.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self._active_worker.start()
        
    def _on_deinterleave_done(self, result_bits):
        self.hex_viewer.update_bits(result_bits)
        self.status_bar.showMessage(f"De-interleaving Complete. Output bits: {len(result_bits)}")
        
        
    def _on_decode_async(self):
        if self.pipeline.state.demod is None:
            return QMessageBox.warning(self, "Warning", "Please run demodulation first.")
            
        params = self.fec_controls.get_params()
        method = params.pop("method")
        
        self.status_bar.showMessage("Decoding...")
        self.viz_tabs.setCurrentIndex(3) # Go to Hex tab
        
        self._active_worker = PipelineWorker(self.pipeline.stage5_fec_decode, method, **params)
        self._active_worker.finished.connect(self._on_decode_done)
        self._active_worker.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self._active_worker.start()
        
    def _on_decode_done(self, result_bits):
        self.hex_viewer.update_bits(result_bits)
        self.status_bar.showMessage(f"FEC Decoding Complete. Output bits: {len(result_bits)}")


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("SignalForge")
    app.setOrganizationName("Team Ramanuja")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
