import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.text as mtext

from NeutroSpecUI.simulate import SimulationResult


class LegendTitle(object):
    def __init__(self, text_props=None):
        self.text_props = text_props or {}
        super(LegendTitle, self).__init__()

    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        title = mtext.Text(
            x0, y0, r"\underline{" + orig_handle + "}", usetex=True, **self.text_props
        )
        handlebox.add_artist(title)
        return title


def plot_volume_fraction(
    res: SimulationResult,
    ax: plt.Axes,
    **kwargs,
):
    fractions = res.extras["fractions"]
    z_axis = res.extras["z_axis"]
    z_axis_lim = res.extras["z_axis_lim"]
    materials = res.extras["materials"]

    kwargs.pop("color", None)
    label_sub_title = kwargs.pop("label", "")
    label_sub_title = label_sub_title + ": " if label_sub_title else ""

    handles, labels = ax.get_legend_handles_labels()

    for i, volume in enumerate(fractions.T):
        line = ax.plot(z_axis, volume, **kwargs)
        handles.append(line[0])
        labels.append(materials[i].name)

    ax.set_title("Volume Fractions")
    ax.set_xlabel("z $(\\AA)$")
    ax.set_ylabel("Volume Fraction")
    ax.set_xlim(z_axis_lim)
    ax.legend(handles, labels)


def plot_sld(
    res: SimulationResult,
    ax: plt.Axes,
    **kwargs,
):
    rho = res.extras["rho"]
    z_axis = res.extras["z_axis"]
    z_axis_lim = res.extras["z_axis_lim"]

    ax.plot(z_axis, rho, label=kwargs.pop("label", "sld"), **kwargs)
    ax.set_title("SLD Profiles")
    ax.set_xlabel("z $(\\AA)$")
    ax.set_ylabel("SLD")
    ax.set_xlim(z_axis_lim)
    ax.legend()


def plot_reflectivity(
    sim: SimulationResult,
    ax: plt.Axes,
    **kwargs,
):
    q_axis = sim.x
    reflectivity = sim.y
    left, right = sim.extras["q_axis_lim"]
    left = None if left == 0 else left

    ax.plot(
        q_axis,
        reflectivity * q_axis**4,
        label=kwargs.pop("label", "sld"),
        **kwargs,
    )
    ax.set_xlabel("$q_z[\\AA^{-1}]$")
    ax.set_ylabel("$Rq_z^4[\\AA^{-4}]$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(left, right)
    ax.legend()


def plot_reflectivity_data(df: pd.DataFrame, ax: plt.Axes, **kwargs):
    # 3rd subplot: Reflectivity
    df["x"] = df["q"]
    df["y"] = df["refl"] * df["q"] ** 4
    df["yerr"] = df["refl_err"] * df["q"] ** 4
    df["xerr"] = df["q_res (FWHM)"] / 2
    df.plot(
        x="x",
        y="y",
        yerr="yerr",
        xerr="xerr",
        kind="scatter",
        ax=ax,
        color="black",
        label="Data",
    )
