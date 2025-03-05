from abc import ABC
from typing import Type
from itertools import chain

import pandas as pd
from matplotlib.axes import Axes

from PySide6.QtCore import QObject

from NeutroSpecUI.simulate import Simulation, SimulationResult


class Backend(ABC):
    """A class to define the backend interface.

    This class defines the interface for the backend. A backend provides custom data parsing, simulation, plotting functions, etc. for the UI. The backend should implement the functions defined here to work with the UI.
    """

    @staticmethod
    def parse_data(df: pd.DataFrame) -> tuple:
        """Parses the data from the read in dataframe.

        The UI will read in a dataframe when the user selects a data file. This function will be called to parse the data to `x, y, sx, sy` (x values, y values, x errors, y errors). sx and sy can be None or left out if the data does not have errors.

        Args:
            df (pd.DataFrame): The dataframe containing the data to parse.

        Returns:
            tuple: A tuple containing the x, y, sx, sy values.
        """
        print(
            "No data parsing function implemented. Check your Backend to implement it."
        )
        return None, None, None, None

    @staticmethod
    def default_settings(sim: Simulation) -> dict:
        """Returns the default settings for the simulation.

        You can define specific settings in the UI which can then be used in the simulation. This function should return a dictionary with the default settings for the simulation.

        Args:
            sim (Simulation): The simulation object to get the default settings for.

        Returns:
            dict: A dictionary containing the default settings for the simulation.
        """
        print(
            "No default settings function implemented. Check your Backend to implement it."
        )
        return {}

    @staticmethod
    def simulate(sim: Simulation) -> SimulationResult | None:
        """Simulates the given simulation object.

        This function should simulate the given simulation object and return a `SimulationResult` object. If the simulation fails, this function should return `None`. It can use the `sim.settings` dictionary to get the settings for the simulation.

        Args:
            sim (Simulation): The simulation object to simulate.

        Returns:
            SimulationResult | None: The result of the simulation or None if the simulation failed.
        """
        print("No simulation function implemented. Check your Backend to implement it.")
        return None

    @staticmethod
    def plot_simulation(res: SimulationResult, axes: list[Axes], **kwargs) -> None:
        """Plots the simulation result.

        Args:
            res (SimulationResult): The simulation result to plot.
            axes (list[Axes]): The list of axes to plot on.
        """
        print(
            "No simulation plot function implemented. Check your Backend to implement it."
        )
        return

    @staticmethod
    def plot_data(df: pd.DataFrame, axes: list[Axes], **kwargs) -> None:
        """Plots the data from the dataframe.

        Args:
            df (pd.DataFrame): The dataframe containing the data to plot.
            axes (list[Axes]): The list of axes to plot on.
        """
        print("No data plot function implemented. Check your Backend to implement it.")
        return


class BackendHandler(QObject):
    """A class to handle the backend functions for the UI.

    This class uses the provided backend to call the functions needed for the UI to work. It is used to abstract the backend from the UI and make it easier to switch between backends.
    """

    _backend: Type[Backend]

    def __init__(
        self, backend: Type[Backend] = Backend, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._backend = backend

    def load_backend(self, backend: Type[Backend]) -> None:
        self._backend = backend

    def plot_simulation(
        self, res: SimulationResult, axes: list[Axes], **kwargs
    ) -> None:
        return self._backend.plot_simulation(res, axes, **kwargs)

    def plot_data(self, df: pd.DataFrame, axes: list[Axes], **kwargs) -> None:
        return self._backend.plot_data(df, axes, **kwargs)

    def parse_data(self, df: pd.DataFrame) -> tuple:
        data = self._backend.parse_data(df)
        if len(data) < 2:
            raise ValueError(
                "Data parsing failed. parse_data should return at least x and y values."
            )
        x, y, sx, sy, *_ = chain(data, [None, None])
        return x, y, sx, sy

    def default_settings(self, sim: Simulation) -> dict:
        return self._backend.default_settings(sim)

    def simulate(self, sim: Simulation) -> SimulationResult | None:
        sim.settings = self.default_settings(sim)
        result = self._backend.simulate(sim)
        if result is None:
            return None
        result.extras.update(sim.settings)
        return result
