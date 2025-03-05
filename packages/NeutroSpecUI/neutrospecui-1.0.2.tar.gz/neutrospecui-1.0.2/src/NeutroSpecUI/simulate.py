from typing import TYPE_CHECKING, cast
from collections.abc import Sequence
from dataclasses import dataclass, field
import copy

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal, QObject

if TYPE_CHECKING:
    from NeutroSpecUI.material import Material
    from NeutroSpecUI.parameter import Parameter
    from NeutroSpecUI.app import NeutroApp


@dataclass
class SimulationResult:
    """Dataclass that holds the results of a simulation.

    Attributes:
        x (np.ndarray): The x values of the simulation.
        y (np.ndarray): The y values of the simulation.
        extras (dict): Dictionary of extra data returned by the simulation.
    """

    x: np.ndarray
    y: np.ndarray
    extras: dict = field(default_factory=dict)

    def __init__(self, x: np.ndarray, y: np.ndarray, **extras):
        self.x = x
        self.y = y
        self.extras = extras


@dataclass
class Simulation:
    """Dataclass that holds the simulation parameters and settings.

    Attributes:
        materials (list["Material"]): List of materials in the simulation.
        static_params (list["Parameter"]): List of static parameters in the simulation.
        settings (dict): Dictionary of settings for the simulation.
    """

    materials: list["Material"]
    static_params: list["Parameter"]
    settings: dict = field(default_factory=dict)

    def __init__(
        self, materials: list["Material"], static_params: list["Parameter"], **settings
    ):
        self.materials = materials
        self.static_params = static_params
        self.settings = settings

    def get_unlocked_parameters(self) -> list["Parameter"]:
        """Returns a list of all unlocked parameters in the simulation."""
        material_params = [
            param
            for material in self.materials
            for param in material.get_parameters()
            if not param.locked
        ]
        static_params = [param for param in self.static_params if not param.locked]
        return static_params + material_params

    def set_by_vector(self, vector: Sequence) -> None:
        """Sets the parameter values in the simulation by a vector of values.

        Args:
            vector (Sequence): The vector of values to set the parameters to. The vector should be the same length as the number of unlocked parameters in the simulation.
        """
        params = self.get_unlocked_parameters()
        for i, param in enumerate(params):
            param.value = vector[i]

    def get_vector(self) -> np.ndarray:
        """Returns a vector of the values of the unlocked parameters in the simulation."""
        return np.array([param.value for param in self.get_unlocked_parameters()])

    def get_bounds(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns a tuple of the lower and upper bounds of the unlocked parameters in the simulation."""
        lower_bounds = np.array(
            [param.bounds[0] for param in self.get_unlocked_parameters()]
        )
        upper_bounds = np.array(
            [param.bounds[1] for param in self.get_unlocked_parameters()]
        )

        return lower_bounds, upper_bounds

    def to_dataframe(self) -> pd.DataFrame:
        """Returns a dataframe of the simulation parameters.

        The dataframe contains the material name, parameter name, locked status, and value of each parameter in the simulation.
        """
        data = []

        for i, param in enumerate(self.static_params):
            data.append(["static", i, param.locked, param.value])

        for material in self.materials:
            for param_name, param in material.get_param_dict().items():
                data.append([material.name, param_name, param.locked, param.value])

        df = pd.DataFrame(
            columns=["material", "parameter", "locked", "value"], data=data
        )
        return df

    def optimize_sim(self, df: pd.DataFrame) -> "Simulation":
        """Optimizes the simulation parameters to fit the data.

        The optimization algorithm fits the simulation results returned by the backend "simulate" function to the data provided by the user. The optimization is done using the scipy curve_fit function and takes the standard deviation of the y values (sy) into account.

        Args:
            df (pd.DataFrame): The dataframe containing the data to fit. This will be parsed to x, y, sx, sy values by the backend "parse_data" function.

        Returns:
            Simulation: A new optimized simulation object.
        """
        sim = copy.deepcopy(self)  # copy the mats so we don't change the original

        app = cast("NeutroApp", QApplication.instance())
        simulate = app.backend.simulate
        parse_data = app.backend.parse_data

        x_real, y_real, sx, sy = parse_data(df)

        def f(x_new, *params):
            sim.set_by_vector(params)
            simulation = simulate(sim)

            if simulation is None:
                raise ValueError(
                    "Simulation failed. Simulate should not return None in fitting. Check your backend."
                )

            return np.interp(x_new, simulation.x, simulation.y)

        init_guess = sim.get_vector()
        print("Initial guess:", init_guess, "\n")

        popt, pcov = curve_fit(
            f,
            x_real,
            y_real,
            p0=init_guess,
            sigma=sy,
            bounds=sim.get_bounds(),
        )

        print("\nOptimal:", popt)
        sim.set_by_vector(popt)

        return sim


class FittingWorker(QObject):
    """Worker class that hosts the fitting algorithm for a separate thread.

    The worker can be moved to a separate thread to avoid blocking the main thread while the fitting algorithm is running. The worker emits a signal when the fitting is finished.

    Attributes:
        resultReady (Signal): Signal emitted when the fitting is finished.
    """

    resultReady = Signal(Simulation)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def doWork(self, df: pd.DataFrame, sim: Simulation) -> None:
        """Runs the fitting algorithm and emits the result signal."""
        opt_sim = sim.optimize_sim(df)
        self.resultReady.emit(opt_sim)


class FittingController(QObject):
    """Controller class for the threading of fitting.

    The controller hosts the worker and the worker thread. It emits a signal when the fitting is finished. It also ensures that only one fitting thread is running at a time and that the fitting thread is properly closed when the application is closed.

    Attributes:
        resultReady (Signal): Signal emitted when the fitting is finished.
    """

    _operate = Signal(pd.DataFrame, Simulation)
    resultReady = Signal(Simulation)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.worker = FittingWorker()
        self.workerThread = QThread(self)
        self.worker.moveToThread(self.workerThread)
        self._operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(self.onResultReady)

        # Closes the fitting thread when the application is closed to prevent internal errors
        app = cast("NeutroApp", QApplication.instance())
        app.aboutToQuit.connect(self.workerThread.quit)
        app.aboutToQuit.connect(self.workerThread.wait)

    def fit(self, df: pd.DataFrame, sim: Simulation) -> None:
        """Starts the fitting algorithm in a separate thread.

        Starting a new fitting thread while another is running will be ignored.

        Args:
            df (pd.DataFrame): The dataframe containing the data to fit.
            sim (Simulation): The simulation object to optimize.
        """
        if self.workerThread.isRunning():
            # TODO: Make a dialog box to inform the user
            print("Fitting thread already running")
            return

        print("Fitting starting")
        self.workerThread.start()
        self._operate.emit(df, sim)

    def onResultReady(self, opt_sim: Simulation) -> None:
        """Slot that receives the fitting result and emits the result signal while closing the fitting thread."""
        self.workerThread.quit()
        self.workerThread.wait()
        self.resultReady.emit(opt_sim)
        print("Fitting finished")

    def deleteLater(self):
        """Closes the fitting thread when the controller is deleted."""
        self.workerThread.quit()
        self.workerThread.wait()
        return super().deleteLater()
