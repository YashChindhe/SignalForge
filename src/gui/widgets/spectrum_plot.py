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

    def set_theme(self, is_dark):
        """Update the matplotlib theme dynamically."""
        bg = '#16213e' if is_dark else '#F8F9FA'
        ax_bg = '#1a1a2e' if is_dark else '#FFFFFF'
        fg = '#eaeaea' if is_dark else '#2B2D42'
        grid = '#0f3460' if is_dark else '#DEE2E6'
        title = '#e94560' if is_dark else '#4361EE'
        line = '#00ff88' if is_dark else '#4361EE'
        
        self.figure.set_facecolor(bg)
        self.ax.set_facecolor(ax_bg)
        self.ax.tick_params(colors=fg)
        self.ax.xaxis.label.set_color(fg)
        self.ax.yaxis.label.set_color(fg)
        for spine in self.ax.spines.values():
            spine.set_color(grid)
        self.ax.title.set_color(title)
        self.ax.grid(True, color=grid, linestyle='--', alpha=0.7)
        self.line.set_color(line)
        self.canvas.draw()
