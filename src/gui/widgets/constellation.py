import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg

class ConstellationWidget(QWidget):
    """PyQtGraph widget for I/Q constellation scatter plot."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Setup PyQtGraph
        pg.setConfigOption('background', '#16213e')
        pg.setConfigOption('foreground', '#eaeaea')
        
        self.plot_widget = pg.PlotWidget(title="I/Q Constellation")
        layout.addWidget(self.plot_widget)
        
        self.plot_widget.setLabel('bottom', "In-Phase (I)")
        self.plot_widget.setLabel('left', "Quadrature (Q)")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Make axes equal aspect ratio
        self.plot_widget.setAspectLocked(True)
        
        # Scatter plot item
        self.scatter = pg.ScatterPlotItem(
            size=5, 
            pen=pg.mkPen(None), 
            brush=pg.mkBrush(233, 69, 96, 180) # #e94560 with alpha
        )
        self.plot_widget.addItem(self.scatter)
        
    def update_plot(self, demod_result):
        """Update the constellation with new DemodResult."""
        self.scatter.setData(x=demod_result.constellation_I, y=demod_result.constellation_Q)
        self.plot_widget.autoRange()

    def set_theme(self, is_dark):
        """Update the pyqtgraph theme dynamically."""
        bg = '#16213e' if is_dark else '#FFFFFF'
        fg = '#eaeaea' if is_dark else '#2B2D42'
        
        self.plot_widget.setBackground(bg)
        # Update axis colors
        self.plot_widget.getAxis('bottom').setPen(fg)
        self.plot_widget.getAxis('bottom').setTextPen(fg)
        self.plot_widget.getAxis('left').setPen(fg)
        self.plot_widget.getAxis('left').setTextPen(fg)
        self.plot_widget.setTitle("I/Q Constellation", color=fg)
