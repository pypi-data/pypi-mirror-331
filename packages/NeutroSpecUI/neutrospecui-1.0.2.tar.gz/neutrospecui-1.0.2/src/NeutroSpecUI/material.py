import pandas as pd
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QApplication

from NeutroSpecUI.parameter import Parameter
from NeutroSpecUI.simulate import Simulation

if TYPE_CHECKING:
    from NeutroSpecUI.app import NeutroApp


@dataclass
class Material:
    # TODO: abstract this class to be more general
    name: str
    thickness: Parameter[float]
    fraction: Parameter[float]
    roughness: Parameter[float]
    rho: Parameter[float]

    def get_parameters(self) -> list[Parameter[float]]:
        self.thickness.bounds = (0, 50)
        self.fraction.bounds = (0, 1)
        self.roughness.bounds = (0, 20)
        self.rho.bounds = (-1e-5, 1e-5)

        return [self.thickness, self.fraction, self.roughness, self.rho]

    def get_param_dict(self) -> dict[str, Parameter[float]]:
        return {
            "thickness": self.thickness,
            "fraction": self.fraction,
            "roughness": self.roughness,
            "rho": self.rho,
        }

    @staticmethod
    def from_dict(data: dict) -> "Material":
        return Material(
            data["name"],
            Parameter(**data["thickness"]),
            Parameter(**data["fraction"]),
            Parameter(**data["roughness"]),
            Parameter(**data["rho"]),
        )


class ExperimentData(QObject):
    """Class to hold all the data for an setup. This includes the data, simulation, and fit.

    Attributes:
        data (pd.DataFrame): The experimental data.
        sim (Simulation): The simulation settings.
        fit (Simulation): The fit settings.
        simulateSim (Signal): Signal to trigger simulation of the simulation.
        simulateFit (Signal): Signal to trigger simulation of the fit.
        updateData (Signal): Signal to trigger update of the data.
        updateSim (Signal): Signal to trigger update of the simulation.
        updateFit (Signal): Signal to trigger update of the fit.
    """

    simulateSim = Signal()
    simulateFit = Signal()

    updateData = Signal()
    updateSim = Signal()
    updateFit = Signal()

    def __init__(
        self,
        data: pd.DataFrame | None,
        materials: list[Material],
        static_params: list[Parameter],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        # TODO: add static parameters
        self.sim = Simulation(materials, static_params)
        self.fit = Simulation(materials, static_params)

        self.data = data

        self._q_axis_lim: tuple | None = None
        self.update_q_axis_lim()

        self.simulateSim.connect(self._simulateSim)
        self.simulateFit.connect(self._simulateFit)

        self.simulateSim.emit()
        self.simulateFit.emit()

    def set_data(self, data: pd.DataFrame | None) -> None:
        self.data = data
        self.update_q_axis_lim()
        self.updateData.emit()

    def set_static_params(self, static_params: list[Parameter]) -> None:
        self.sim.static_params = static_params
        self.simulateSim.emit()

    def set_materials(self, materials: list[Material]) -> None:
        self.sim.materials = materials
        self.simulateSim.emit()

    def set_fit_sim(self, opt_sim: Simulation) -> None:
        self.fit = opt_sim
        self.simulateFit.emit()

    @Slot()
    def _simulateSim(self) -> None:
        app = cast("NeutroApp", QApplication.instance())
        self.sim_result = app.backend.simulate(self.sim)
        self.updateSim.emit()

    @Slot()
    def _simulateFit(self) -> None:
        app = cast("NeutroApp", QApplication.instance())
        self.fit_result = app.backend.simulate(self.fit)
        self.updateFit.emit()

    def update_q_axis_lim(self, padding_factor: float = 1.25):
        if self.data is None:
            return

        lim = (
            self.data["q"].min() / padding_factor,
            self.data["q"].max() * padding_factor,
        )

        if lim == self._q_axis_lim:
            return
        self._q_axis_lim = lim

        self.sim.settings["q_axis_lim"] = self._q_axis_lim
        self.fit.settings["q_axis_lim"] = self._q_axis_lim

        app = cast("NeutroApp", QApplication.instance())
        self.sim_result = app.backend.simulate(self.sim)
        self.fit_result = app.backend.simulate(self.fit)
