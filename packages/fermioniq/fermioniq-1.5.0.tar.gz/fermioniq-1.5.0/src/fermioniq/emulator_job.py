"""The fermioniq.emulator_job module contains classes to set up jobs.

the computational tasks that you want to send to the quantum circuit emulator.
These contain information about the circuit(s) to be run,
parameters for the emulator, and more.
"""

import sys
from typing import Any, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
    field_validator,
    model_validator,
)
from rich.console import Group
from rich.panel import Panel

from fermioniq.config.defaults import standard_config
from fermioniq.custom_logging.printing import (
    MIDDLE_GRAY,
    OUTER_GRAY,
    rich_amplitudes,
    rich_expectations,
    rich_global_metadata,
    rich_metadata,
    rich_mps,
    rich_optimizer,
    rich_samples,
    rich_trajectories,
)
from qcshared.config.config_utils import print_error_warning_table
from qcshared.config.constants import MAX_JOB_SIZE
from qcshared.config.emulator_config import EmulatorConfig
from qcshared.config.emulator_input import EmulatorInput
from qcshared.json.decode import dejsonify
from qcshared.json.encode import compress_json, jsonify, wrap_noise_model
from qcshared.json.utils import dicts_equal, recursive_dict_update
from qcshared.noise_models import NoiseModel
from qcshared.serializers.circuit import SerializedCircuit
from qcshared.serializers.custom_types import (
    Circuit,
    CirqCircuit,
    QiskitCircuit,
    is_qiskit_cirq_circuit,
)
from qcshared.serializers.serializer import serialize_circuit, serialize_config


# DOCUMENT EmulatorJob class with examples
class EmulatorJob(BaseModel):
    """Class for setting up jobs that can be sent with the :py:meth:`~fermioniq.client.Client`.

    Attributes
    ----------
    circuit
        A cirq.circuits.circuit.Circuit or a qiskit QuantumCircuit, or a list of circuits.
    config
        Emulator configuration, or a list of configurations (one for each circuit).
    noise_model
        A string of a remote noise model or a dict containing a noise model or None.
    remote_config
        Name of the remote execution engine to use.
    project
        Name of the project to use. Can be None.
    notification_mode
        Where to send a notification when job is finished. Can be 'slack', 'email' or None.
    label
        Job label or name. Can be None.
    """

    circuit: list[Any]
    config: list[dict[str, Any]] = Field(default=[{}], validate_default=True)
    noise_model: list[Optional[str | NoiseModel]] = Field(
        default=[None], validate_default=True
    )
    remote_config: Optional[str | dict[str, Any]] = None
    project: Optional[str] = None
    notification_mode: Optional[Literal["slack", "email"]] = None
    label: Optional[str] = Field(default=None, max_length=40)
    _job_id: str = PrivateAttr(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, value):
        self._job_id = value

    @field_validator("circuit", "config", "noise_model", mode="before")
    @classmethod
    def validate_fields(cls, v, info):
        if not isinstance(v, list):
            v = [v]
        if info.field_name == "circuit" and len(v) > MAX_JOB_SIZE:
            raise ValueError(
                f"Too many circuits for this job (got {len(v)} while max {MAX_JOB_SIZE} are allowed)"
            )
        return v

    @field_validator("config", "noise_model", mode="after")
    @classmethod
    def validate_config_noisemodel_post(cls, v, info):
        circuit = info.data["circuit"]
        if v == [None]:
            v = [None] * len(circuit)
        elif len(v) == 1 and info.field_name == "config":
            v = [v[0].copy() for _ in range(len(circuit))]
        elif len(v) == 1 and info.field_name == "noise_model":
            v = [v[0].model_copy() for _ in range(len(circuit))]
        if len(v) != len(circuit):
            raise ValueError(
                f"Number of {info.field_name}s provided ({len(v)}) does not match the number of circuits ({len(circuit)})."
            )
        return v

    @model_validator(mode="after")
    def serialize_inputs(self):
        # We serialize every circuit and config, and validate every circuit, config, and noise model
        all_inputs = []
        for circ, conf, noise_model in zip(self.circuit, self.config, self.noise_model):
            # Always make a standard config, and update it with the user-provided one (if possible)
            standard_conf = standard_config(
                circ, effort=0.1, noise=(noise_model is not None)
            )
            default_qubit_objects = standard_conf["qubits"]

            # Update the config with the user-provided one
            if conf is None:
                conf = {}
            final_conf = recursive_dict_update(standard_conf, conf)

            # If this update set 'qubits' to None, we put the default qubit order there
            if final_conf["qubits"] is None:
                final_conf["qubits"] = default_qubit_objects

            # Fully serialize the config
            final_conf = serialize_config(final_conf)

            try:
                # Serialize the circuit
                serialized_circuit = serialize_circuit(
                    circuit=circ,
                    third_party_serialization=final_conf["mode"] == "statevector",
                )
                emulator_input = EmulatorInput(
                    emulator_config=final_conf,
                    serialized_circuit=serialized_circuit,
                    noise_model=noise_model,
                )
                all_inputs.append(emulator_input)
            except ValidationError as e:
                # TODO: If verbosity is high, print the errors during validation
                # if verbose:
                print_error_warning_table("Input errors", e.errors(), title_color="red")
                sys.exit(1)

            if not (
                all(input.emulator_config.mode == "statevector" for input in all_inputs)
                or all(
                    input.emulator_config.mode != "statevector" for input in all_inputs
                )
            ):
                raise ValueError(
                    "Configs in an EmulatorJob should either all use statevector mode, or all not use statevector mode"
                )

        self.config = [input.emulator_config for input in all_inputs]
        self.noise_model = [input.noise_model for input in all_inputs]
        self.circuit = [input.serialized_circuit for input in all_inputs]

        return self


class JobResult(BaseModel):
    status_code: int
    label: Optional[str] = None
    job_outputs: list[dict[str, Any]]
    job_metadata: dict[str, Any]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dejsonify the job_outputs and job_metadata
        self.job_outputs = dejsonify(self.job_outputs)
        self.job_metadata = dejsonify(self.job_metadata)

        # Populate the configs of the job_output dicts from the job_metadata unique_configs
        #  and then remove the unique_configs field from the job_metadata
        unique_configs = self.job_metadata["unique_configs"]
        for emulation_output in self.job_outputs:
            emulation_output["config"] = unique_configs[emulation_output["config"]]
        self.job_metadata.pop("unique_configs")

    def _extract_field(
        self,
        circuit_number: int,
        run_number: int,
        field: str,
    ) -> Any | None:
        """
        Extract a field from a list of results.

        Parameters
        ----------
        circuit_number
            Circuit number.
        run_number
            Run number.
        field
            Field to extract.
        """
        for output in self.job_outputs:
            if (
                output["circuit_number"] == circuit_number
                and output["run_number"] == run_number
            ):
                if field in output["output"]:
                    return output["output"][field]
                elif field in output:
                    return output[field]

        return None

    def amplitudes(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number, run_number=run_number, field="amplitudes"
        )

    def samples(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number, run_number=run_number, field="samples"
        )

    def run_metadata(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number, run_number=run_number, field="metadata"
        )

    def config(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number, run_number=run_number, field="config"
        )

    def trajectories(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number, run_number=run_number, field="trajectories"
        )

    def expectation_values(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number,
            run_number=run_number,
            field="expectation_values",
        )

    def optimizer_data(self, circuit_number: int, run_number: int):
        return self._extract_field(
            circuit_number=circuit_number,
            run_number=run_number,
            field="optimizer_history",
        )

    def __str__(self) -> str:
        return str(
            {
                "job_label": self.label,
                "job_outputs": self.job_outputs,
                "job_metadata": self.job_metadata,
            }
        )

    def __rich__(self):
        # Assumptions on the output format: a list of dicts, each with a circuit number, run number, output
        #  dict, metadata dict and config specific to the run.
        all_data = (
            (
                r["circuit_number"],
                r["run_number"],
                r["output"],
                r["metadata"],
                r["config"],
            )
            for r in self.job_outputs
        )
        all_data_sorted = sorted(all_data, key=lambda x: (x[0], x[1]))

        all_rich_groups = []
        curr_circuit_number = -1
        circuit_groups = (
            []
        )  # List of result and metadata panels per run, for the current circuit.
        for (
            next_circuit_number,
            run_number,
            output,
            metadata,
            config,
        ) in all_data_sorted:
            amplitudes = output.get("amplitudes", None)
            samples = output.get("samples", None)
            expectation_values = output.get("expectation_values", None)
            mps = output.get("mps", None)
            optimizer_history = output.get("optimizer_history", None)
            trajectories = output.get("trajectories", None)

            # Put all circuits into a single panel
            if curr_circuit_number != next_circuit_number:
                # Make a panel for all runs of the previous circuit
                if len(circuit_groups) > 0:
                    circuit_title = f"[bold]Circuit {curr_circuit_number}[/bold]"
                    circuit_panel = Panel(
                        Group(*circuit_groups),
                        title=circuit_title,
                        border_style=OUTER_GRAY,
                        title_align="left",
                    )
                    all_rich_groups.append(circuit_panel)
                curr_circuit_number = next_circuit_number
                circuit_groups = []

            run_title = f"[bold]Run {run_number}[/bold]"

            # Amplitudes panel
            # Decide whether this was a noisy emulation or not by inspecting the config (if possible)
            noise = False
            if config:
                noise = config["noise"].get("enabled", False)

            amplitude_panel = (
                rich_amplitudes(amplitudes, metadata, noise=noise)
                if amplitudes
                else None
            )

            # Samples panel
            sample_panel = rich_samples(samples, metadata) if samples else None

            exp_val_panel = (
                rich_expectations(expectation_values, metadata)
                if expectation_values
                else None
            )

            mps_panel = rich_mps(mps) if mps else None

            # Metadata panel
            metadata_panel = rich_metadata(metadata, config)

            # Optimizer history panel
            optimizer_panel = (
                rich_optimizer(optimizer_history) if optimizer_history else None
            )

            # Trajectory panel
            trajectories_panel = (
                rich_trajectories(trajectories) if trajectories else None
            )

            result_panels = [
                p
                for p in [
                    optimizer_panel,
                    trajectories_panel,
                    amplitude_panel,
                    sample_panel,
                    exp_val_panel,
                    mps_panel,
                ]
                if p is not None
            ]

            if not result_panels:
                if not output:
                    group = Group(
                        "[red][bold]No output available[/bold]\n",
                    )
                else:
                    group = Group(
                        "[red][bold]Unexpected results. Printing raw output instead:[/bold]",
                        str(output),
                    )
                circuit_groups.append(
                    Panel(
                        Group(group, metadata_panel),
                        title=run_title,
                        border_style=MIDDLE_GRAY,
                        title_align="left",
                    )
                )
            else:
                # Add the group (for the run) to the list of groups for this circuit
                circuit_groups.append(
                    Panel(
                        Group(*result_panels, metadata_panel),
                        title=run_title,
                        border_style=MIDDLE_GRAY,
                        title_align="left",
                    )
                )

        # Add the final circuit panel
        if len(circuit_groups) > 0:
            circuit_title = f"[bold]Circuit {curr_circuit_number}[/bold]"
            circuit_panel = Panel(
                Group(*circuit_groups),
                title=circuit_title,
                border_style=OUTER_GRAY,
                title_align="left",
            )
            all_rich_groups.append(circuit_panel)

        # Make a panel for the metadata for all runs
        global_metadata = self.job_metadata
        global_panel = rich_global_metadata(global_metadata, self.label)

        return Group(*all_rich_groups, global_panel)


def jsonify_and_compress_inputs(
    job: EmulatorJob,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any] | None]]:
    """
    Wrap the configs, circuits, and noise models of an EmulatorJob in JSON.

    For configs and noise models, if all are equal, only one is sent. For circuits, all are compressed.

    Parameters
    ----------
    job
        The EmulatorJob to extract input data from.

    Returns
    -------
    json_circuits
        List of compressed jsonified circuits.

    json_configs
        List of jsonified configs.

    json_noise_models
        List of jsonified noise models, or list of None.
    """
    # Convert configs, noise models, and circuits to JSON
    json_circuits = [jsonify(circuit) for circuit in job.circuit]
    json_configs = [jsonify(config) for config in job.config]
    json_noise_models = [wrap_noise_model(jsonify(noise)) for noise in job.noise_model]

    # Compress the circuit
    json_circuits = ["__compressed__", compress_json(json_circuits)]

    # If all configs are equal, we only need to send one of them
    all_configs_equal = all(dicts_equal(json_configs[0], cfg) for cfg in json_configs)
    if all_configs_equal:
        json_configs = [json_configs[0]]

    # If all noise models are equal, we only need to send one of them
    all_noise_models_equal = all(nm is None for nm in json_noise_models) or (
        isinstance(json_noise_models[0], dict)
        and all(
            isinstance(nm, dict) and dicts_equal(nm, json_noise_models[0])
            for nm in json_noise_models
        )
    )
    if all_noise_models_equal:
        json_noise_models = [json_noise_models[0]]

    return json_circuits, json_configs, json_noise_models
