import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg

class WaterfallPlotWidget(QWidget):
    """PyQtGraph widget for high-performance spectrogram (waterfall) plotting."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Setup PyQtGraph
        pg.setConfigOption('background', '#16213e')
        pg.setConfigOption('foreground', '#eaeaea')
        
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        
        self.plot_widget.setLabel('bottom', "Frequency (Hz)")
        self.plot_widget.setLabel('left', "Time (s)")
        
        # Image item for heatmap
        self.img = pg.ImageItem()
        self.plot_widget.addItem(self.img)
        
        # Colormap (viridis-like)
        colormap = pg.colormap.get('viridis')
        self.img.setColorMap(colormap)
        
    def update_plot(self, spectral_data):
        """Update the waterfall with new SpectralResult data."""
        # Note: pyqtgraph expects image data as (x, y) which is (freqs, times)
        # Sxx is usually (freqs, times) from scipy.spectrogram
        # We need to transpose it to match pyqtgraph's expected orientation
        heatmap_data = spectral_data.spectrogram_power.T
        
        self.img.setImage(heatmap_data, autoLevels=True)
        
        # Set scale and position based on freqs and times
        freq_range = spectral_data.spectrogram_freqs[-1] - spectral_data.spectrogram_freqs[0]
        time_range = spectral_data.spectrogram_times[-1] - spectral_data.spectrogram_times[0]
        
        # Transform the image to align with axes
        tr = pg.QtGui.QTransform()
        tr.translate(spectral_data.spectrogram_freqs[0], spectral_data.spectrogram_times[0])
        tr.scale(freq_range / len(spectral_data.spectrogram_freqs), 
                 time_range / len(spectral_data.spectrogram_times))
        
        self.img.setTransform(tr)

    def set_theme(self, is_dark):
        """Update the pyqtgraph theme dynamically."""
        bg = '#16213e' if is_dark else '#FFFFFF'
        fg = '#eaeaea' if is_dark else '#2B2D42'
        
        self.plot_widget.setBackground(bg)
        self.plot_widget.getAxis('bottom').setPen(fg)
        self.plot_widget.getAxis('bottom').setTextPen(fg)
        self.plot_widget.getAxis('left').setPen(fg)
        self.plot_widget.getAxis('left').setTextPen(fg)
