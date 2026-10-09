import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SpectrumPlotWidget(QWidget):
    """Matplotlib embedded widget for FFT and PSD plotting."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Setup Matplotlib Figure and Canvas
        self.figure = Figure(facecolor='#16213e')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Add a subplot for PSD
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1a1a2e')
        self.ax.tick_params(colors='#eaeaea')
        self.ax.xaxis.label.set_color('#eaeaea')
        self.ax.yaxis.label.set_color('#eaeaea')
        for spine in self.ax.spines.values():
            spine.set_color('#0f3460')
            
        self.ax.set_title("Power Spectral Density", color='#e94560')
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Power (dB/Hz)")
        self.ax.grid(True, color='#0f3460', linestyle='--', alpha=0.7)
        
        self.line, = self.ax.plot([], [], color='#00ff88', linewidth=1.5)
        self.canvas.draw()
        
    def update_plot(self, spectral_data):
        """Update the plot with new SpectralResult data."""
        self.line.set_data(spectral_data.freqs_psd, spectral_data.psd)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
