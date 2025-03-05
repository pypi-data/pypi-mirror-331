from typing import TYPE_CHECKING, cast

import pandas as pd
import matplotlib

matplotlib.use("QtAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QGroupBox,
    QButtonGroup,
    QPushButton,
    QApplication,
)
from PySide6.QtCore import Signal

from NeutroSpecUI.material import ExperimentData
from NeutroSpecUI.simulate import SimulationResult

if TYPE_CHECKING:
    from NeutroSpecUI.app import NeutroApp


class CanvasWidget(FigureCanvasQTAgg):

    def __init__(
        self,
        parent: QWidget | None = None,
        width: float = 5,
        height: float = 4,
        dpi: float | None = 100,
    ) -> None:
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = [self.fig.add_subplot(1, 3, i) for i in range(1, 4)]

        super().__init__(self.fig)
        if parent is not None:
            self.setParent(parent)

    def setParent(self, parent: QWidget | None) -> None:
        self._parent = parent

    def parent(self) -> QWidget | None:
        return self._parent

    def clear(self) -> None:
        for ax in self.axes:
            ax.clear()
        self.draw()


class PlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        # TODO: fix starting at the correct index instead of 0
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.setMinimumHeight(300)

        self.canvas = CanvasWidget(self)
        self.toolbar = NavigationToolbar2QT(canvas=self.canvas, parent=self)

        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.canvas)
        self.setLayout(self.main_layout)

    def plot_sim(
        self,
        res: SimulationResult | None = None,
        df: pd.DataFrame | None = None,
        clear: bool = True,
        **kwargs,
    ) -> None:
        if clear:
            self.canvas.clear()

        app = cast("NeutroApp", QApplication.instance())

        if df is not None:
            app.backend.plot_data(df, axes=self.canvas.axes, **kwargs)

        if res is not None:
            app.backend.plot_simulation(res, axes=self.canvas.axes, **kwargs)

        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def display_loading(self) -> None:
        self.canvas.clear()
        for ax in self.canvas.axes:
            ax.text(0.5, 0.5, "Loading...", ha="center", va="center")
        self.canvas.fig.tight_layout()
        self.canvas.draw()


class PlotWidgetStacked(QStackedWidget):
    def __init__(self, exp_data: ExperimentData, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.exp_data = exp_data
        self.exp_data.updateData.connect(self.plot_sim)
        self.exp_data.updateData.connect(self.plot_fit)
        self.exp_data.updateData.connect(self.plot_compare)
        self.exp_data.updateSim.connect(self.plot_sim)
        self.exp_data.updateSim.connect(self.plot_compare)
        self.exp_data.updateFit.connect(self.plot_fit)
        self.exp_data.updateFit.connect(self.plot_compare)

        self.plots = {
            "simulate": PlotWidget(),
            "fit": PlotWidget(),
            "compare": PlotWidget(),
        }

        for plot_name, plot_widget in self.plots.items():
            self.addWidget(plot_widget)
            plot_widget.setObjectName(plot_name)

    def plot_sim(self) -> None:
        self.plots["simulate"].plot_sim(
            self.exp_data.sim_result, self.exp_data.data, color="blue", label="Sim"
        )

    def plot_fit(self) -> None:
        self.plots["fit"].plot_sim(
            self.exp_data.fit_result, self.exp_data.data, color="red", label="Fit"
        )

    def plot_compare(self) -> None:
        self.plots["compare"].plot_sim(
            self.exp_data.fit_result,
            self.exp_data.data,
            clear=True,
            color="red",
            label="Fit",
        )
        self.plots["compare"].plot_sim(
            self.exp_data.sim_result,
            clear=False,
            color="blue",
            label="Sim",
        )

    def display_loading(self) -> None:
        self.plots["fit"].display_loading()
        self.plots["compare"].display_loading()

    def update_plot_layout(self) -> None:
        for plot in self.plots.values():
            plot.canvas.fig.tight_layout()
            plot.canvas.draw()


class PlotButtons(QGroupBox):
    """
    Displays a group of three buttons for the three different plots.
    """

    idClicked = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(5, 0, 5, 5)
        self.setTitle("Select the plot view")
        self.setObjectName("plotViewOptions")

        self.btn_group = QButtonGroup(self.main_layout)
        self.btn_group.idClicked.connect(self.idClicked)

        self.simulate_btn = QPushButton("Simulate", self)
        self.simulate_btn.setObjectName("simulateViewBtn")
        self.simulate_btn.setCheckable(True)
        self.simulate_btn.setChecked(True)
        self.main_layout.addWidget(self.simulate_btn)
        self.btn_group.addButton(self.simulate_btn, 0)

        self.fit_btn = QPushButton("Fit", self)
        self.fit_btn.setObjectName("fitViewBtn")
        self.fit_btn.setCheckable(True)
        self.main_layout.addWidget(self.fit_btn)
        self.btn_group.addButton(self.fit_btn, 1)

        self.compare_btn = QPushButton("Compare", self)
        self.compare_btn.setObjectName("compareViewBtn")
        self.compare_btn.setCheckable(True)
        self.main_layout.addWidget(self.compare_btn)
        self.btn_group.addButton(self.compare_btn, 2)

        self.setLayout(self.main_layout)
