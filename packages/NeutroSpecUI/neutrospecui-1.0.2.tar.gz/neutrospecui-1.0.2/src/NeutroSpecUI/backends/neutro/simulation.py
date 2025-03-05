import numpy as np
from scipy import special

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NeutroSpecUI.material import Material


def get_binned(arr: np.ndarray, bin_width: int, repeat: bool = False) -> np.ndarray:
    n_bins = len(arr) // bin_width
    trimmed_arr = arr[: bin_width * n_bins]
    meaned: np.ndarray = trimmed_arr.reshape((n_bins, bin_width)).mean(axis=1)
    if repeat:
        return np.repeat(meaned, bin_width)
    return meaned


def get_fractions(
    materials: list["Material"], z_axis: np.ndarray, start_roughness: float = 0.1
) -> np.ndarray:
    if not materials:
        raise ValueError("The materials list is empty")

    sigmas = np.array([start_roughness] + [mat.roughness.value for mat in materials])
    thicknesses = np.array([mat.thickness.value for mat in materials])
    positions = np.cumsum(
        [-materials[0].thickness.value]
        + [mat.thickness.value for mat in materials][:-1]
    )
    fractions: np.typing.NDArray[np.float64] = np.array(
        [mat.fraction.value for mat in materials]
    )

    start: np.typing.NDArray[np.float64] = z_axis[:, np.newaxis] - positions
    stop: np.typing.NDArray[np.float64] = start - thicknesses

    sigmas_scaled = sigmas * np.sqrt(2)
    step_ups = special.erf(start / sigmas_scaled[:-1])
    step_downs = special.erf(stop / sigmas_scaled[1:])

    volume: np.typing.NDArray[np.float64] = (step_ups - step_downs) / 2
    return fractions * volume


def convolution(qs, q, delta_q_axis):
    width = delta_q_axis / (2 * np.sqrt(2 * np.log(2)))
    return np.exp(-((qs - q) ** 2) / (2.0 * width**2))


def convolution_refl(
    rho: np.ndarray,
    q_axis: np.ndarray,
    rho_bin_size: int = 1,
    mult: int = 3,
):
    if not rho_bin_size == 1:
        rho = get_binned(rho, bin_width=rho_bin_size)

    # why do we multipy with 3?
    n_qs = mult * len(q_axis)
    qs = q_axis[0] * (q_axis[-1] / q_axis[0]) ** np.linspace(0, 1, n_qs)

    refl = np.array([get_reflectivity(q, rho, rho_bin_size) for q in qs])

    delta_qz = q_axis[1] - q_axis[0]

    new_refl = np.zeros_like(q_axis)

    for i in range(len(q_axis)):
        # where does this come from?
        indices = np.where(np.abs(qs - q_axis[i]) <= 4 * delta_qz)[0]
        weights = convolution(qs[indices], q_axis[i], 2 * delta_qz)
        factors = weights / np.sum(weights)
        new_refl[i] = np.sum(np.real_if_close(refl[indices] * factors))

    return new_refl


def get_reflectivity(q: int, rho: np.ndarray, rho_bin_size: int) -> np.float64:
    ci = complex(0, 1)
    c1 = complex(1, 0)
    c0 = complex(0, 0)
    k0 = complex(q / 2)

    # q_z = 4 * pi / lambda * sin(theta_i)
    k = np.sqrt(k0**2 - 4 * np.pi * (rho - rho[0]))

    rfres = (k[:-1] - k[1:]) / (k[:-1] + k[1:])

    d = rho_bin_size
    # why dont we use hphase?
    # hphase = np.exp(ci * k[1:] * d)
    fphase = np.exp(2 * ci * k[1:] * d)

    rp = np.zeros(len(rho), dtype=np.complex128)
    rp[-1] = c0
    rp[-2] = rfres[-1]
    for i2 in range(len(rho) - 3, -1, -1):
        rp[i2] = (rfres[i2] + rp[i2 + 1] * fphase[i2]) / (
            c1 + rfres[i2] * rp[i2 + 1] * fphase[i2]
        )

    reflectivity: np.float64 = np.abs(rp[0]) ** 2
    return reflectivity
