from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable

class PipelineWorker(QThread):
    """
    Generic worker thread for running pipeline stages 
    without blocking the GUI event loop.
    """
    finished = pyqtSignal(object)    # Emits the result
    error = pyqtSignal(str)          # Emits error message
    progress = pyqtSignal(int)       # 0-100 progress
    
    def __init__(self, task: Callable, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.task(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
