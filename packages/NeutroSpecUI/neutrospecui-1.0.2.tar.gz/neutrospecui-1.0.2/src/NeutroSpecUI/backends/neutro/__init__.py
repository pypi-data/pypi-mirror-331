import numpy as np
import pandas as pd

from NeutroSpecUI.backends import Backend
from NeutroSpecUI.backends.neutro import simulation, plot
from NeutroSpecUI.simulate import Simulation, SimulationResult


class NeutroBackend(Backend):
    @staticmethod
    def parse_data(df: pd.DataFrame):
        x_real = df["q"].values
        y_real = df["refl"].values
        sx = df["q_res (FWHM)"].values
        sy = df["refl_err"].values

        return x_real, y_real, sx, sy

    @staticmethod
    def default_settings(sim: Simulation):
        z_axis_factor = sim.settings.get("z_axis_factor", 1.25)

        q_axis_lim = sim.settings.get("q_axis_lim", (0, 0.3))
        if q_axis_lim[0] < 0 or q_axis_lim[1] < q_axis_lim[0]:
            raise ValueError(
                "qz start should not be negative or smaller than the qz stop"
            )

        z_axis_lim: tuple[float, float]
        if len(sim.materials) == 0:
            z_axis_lim = (0, 1)
        elif len(sim.materials) == 1:
            z_axis_lim = (
                0,
                sim.materials[0].thickness.value + sim.materials[0].roughness.value + 1,
            )
        else:
            mat_width = (
                sum([mat.thickness.value for mat in sim.materials[1:-1]])
                + sim.materials[0].roughness.value
                + sim.materials[-1].roughness.value
            )
            z_axis_lim = (
                mat_width * (1 - z_axis_factor),
                mat_width * z_axis_factor + 1,
            )

        return {
            "z_axis_lim": z_axis_lim,
            "q_axis_lim": q_axis_lim,
            "delta_q_axis": 0.001,
            "z_axis_factor": z_axis_factor,
        }

    @staticmethod
    def simulate(sim: Simulation):
        if len(sim.materials) < 2:
            # We need at least one material and the fluid
            return None

        # Create axes
        z_axis = np.arange(
            sim.settings["z_axis_lim"][0], sim.settings["z_axis_lim"][1] + 1
        )
        q_axis = np.arange(
            sim.settings["q_axis_lim"][0],
            sim.settings["q_axis_lim"][1],
            sim.settings["delta_q_axis"],
        )[1:]

        fractions = simulation.get_fractions(sim.materials[:-1], z_axis)
        fluid_fraction = 1 - np.sum(fractions, axis=1)
        fractions = np.hstack((fractions, fluid_fraction[:, np.newaxis]))

        rhos = np.array([mat.rho.value for mat in sim.materials])

        rho = np.sum(fractions * rhos, axis=1)
        reflectivity = simulation.convolution_refl(rho, q_axis)

        y = reflectivity * sim.static_params[0].value + sim.static_params[1].value

        return SimulationResult(
            x=q_axis,
            y=y,
            fractions=fractions,
            rho=rho,
            z_axis=z_axis,
            materials=sim.materials,
        )

    @staticmethod
    def plot_simulation(res: SimulationResult, axes, **kwargs):
        plot.plot_volume_fraction(res, ax=axes[0], **kwargs)
        plot.plot_sld(res, ax=axes[1], **kwargs)
        plot.plot_reflectivity(res, ax=axes[2], **kwargs)

    @staticmethod
    def plot_data(df: pd.DataFrame, axes, **kwargs):
        plot.plot_reflectivity_data(df, ax=axes[2], **kwargs)
