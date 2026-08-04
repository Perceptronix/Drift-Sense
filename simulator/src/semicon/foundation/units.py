"""Physical constants and unit conversions (Phase 2.1 / 4.4).

All lengths inside the simulation are nanometres; all energies keV.
"""
from __future__ import annotations

# --- Physical constants (CODATA, fixed) ---
C_LIGHT = 299_792_458.0  # m/s
M_ELECTRON_KG = 9.1093837015e-31
E_CHARGE_C = 1.602176634e-19
H_PLANCK_JS = 6.62607015e-34

# --- Unit conversions ---
NM_TO_M = 1e-9
M_TO_NM = 1e9
EV_TO_KEV = 1e-3
KEV_TO_EV = 1e3
PICO_TO_AMP = 1e-12

# --- Electron-optical relations ---
def electron_wavelength_keV(energy_keV: float) -> float:
    """Non-relativistic de Broglie wavelength in nm."""
    import math

    E = energy_keV * KEV_TO_EV * E_CHARGE_C  # J
    p = math.sqrt(2.0 * M_ELECTRON_KG * E)
    lam = H_PLANCK_JS / p  # m
    return lam * M_TO_NM


def energy_from_wavelength_nm(lam_nm: float) -> float:
    """Inverse of electron_wavelength_keV (relativistic correction included)."""
    import math

    lam = lam_nm * NM_TO_M
    a = E_CHARGE_C / (2.0 * M_ELECTRON_KG * C_LIGHT**2)
    g = H_PLANCK_JS**2 / (2.0 * M_ELECTRON_KG * lam**2 * E_CHARGE_C * E_CHARGE_C)
    E_keV = (math.sqrt(1.0 + 4.0 * a * g) - 1.0) / (2.0 * a) * KEV_TO_EV
    return E_keV


def pa_to_electrons_per_second(probe_current_pA: float) -> float:
    """Probe current in pA -> electrons per second."""
    return (probe_current_pA * PICO_TO_AMP) / E_CHARGE_C
