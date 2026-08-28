from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, largura: float = 5, altura: float = 3.2, dpi: int = 100):
        self.figure = Figure(figsize=(largura, altura), dpi=dpi, tight_layout=True)
        super().__init__(self.figure)

    def limpar(self):
        self.figure.clear()
        return self.figure.add_subplot(111)
