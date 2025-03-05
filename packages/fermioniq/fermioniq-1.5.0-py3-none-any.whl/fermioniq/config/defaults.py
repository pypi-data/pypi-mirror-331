"""The fermioniq.config.defaults module contains functions for generating standard configuration settings for different types of emulations.
"""

from typing import Any

from qcshared.config.defaults import standard_config_impl
from qcshared.noise_models import NoiseModel
from qcshared.noise_models.channel import DepolarizingChannel
from qcshared.serializers.circuit import SerializedCircuit
from qcshared.serializers.custom_types import Circuit


def standard_config_noisy(circuit: Circuit, effort: float = 0.1) -> dict[str, Any]:
    """Given a circuit return a default config setup that should perform well on a noisy emulation of this circuit.

    The effort parameter is used to control how much computational effort will be put into emulating
    this circuit. More effort will usually mean higher fidelity, although it depends on the difficulty
    of the circuit.

    Parameters
    ----------
    circuit :
        The circuit (from Cirq / Qiskit).
    effort :
        A float between 0 and 1 that specifies the 'effort' that should be put into emulation.
        A number closer to 1 will aim to maximize fidelity of the emulation (up to memory limitations).

    Returns
    -------
    config
        Updated emulator input with standard settings.
    """
    return standard_config(circuit, effort, True)


def standard_config(
    circuit: Circuit | SerializedCircuit,
    effort: float = 0.1,
    noise: bool = False,
) -> dict[str, Any]:
    """Given a circuit in qiskit or cirq, return a default config setup that should perform well on this circuit.

    The effort parameter is used to control how much computational effort will be put into emulating
    this circuit. More effort will usually mean higher fidelity, although it depends on the difficulty
    of the circuit.

    Parameters
    ----------
    circuit :
        The circuit.
    effort :
        A float between 0 and 1 that specifies the 'effort' that should be put into emulation.
        A number closer to 1 will aim to maximize fidelity of the emulation (up to memory limitations).
    noise :
        Indicate whether this is a noisy simulation or not.

    Returns
    -------
    config
        Emulator config with standard settings.
    """
    config = standard_config_impl(circuit, effort, noise)
    return config
