import json
from typing import Any, ItemsView, Optional, cast

import numpy as np
import rich
from rich import box, print
from rich.console import Group
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import Progress, SpinnerColumn, TaskID, TimeElapsedColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from qcshared.config.config_utils import print_error_warning_table
from qcshared.json.decode import CustomDecoder
from qcshared.messaging.message import (
    ConfigMessage,
    ErrorMessage,
    ProgressMessage,
    StringMessage,
)

# Store colors for rich printing
OUTER_GRAY = "gray89"
MIDDLE_GRAY = "gray70"
INNER_GRAY = "gray50"

# DOCUMENT THIS


class FermioniqSpinner(Spinner):
    FRAMES = " ⡀⡠⡤⡦⡮⡯⡯⡯⡯"
    FRAMES += FRAMES[::-1]

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.frames = cast(list[str], self.FRAMES)[:]


class Printer:
    progress_bar: Optional[Progress]
    task: Optional[TaskID]

    def __init__(self) -> None:
        self.progress_bar = None
        self.tasks: dict[str, TaskID] = dict()

    def _update_progress(self, abs_value: float, label: str, color: str = "red"):
        """Starts or updates progress bars.

        Parameters
        ----------
        abs_value
            Current progress (0.0-1.0).
        label
            Label to be printed next to the progress bar. The label also serves
            as a unique identifier for each progress bar.
        color
            Color of the label.
        """
        if self.progress_bar is None:
            # Spinner left of the progress bar
            spinner_column = SpinnerColumn()
            spinner_column.spinner = FermioniqSpinner("dots")
            self.progress_bar = Progress(
                spinner_column,
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                transient=False,
            )

        if label not in self.tasks:
            self.tasks[label] = self.progress_bar.add_task(
                f"[{color}]{label}...", total=1.0
            )
            self.progress_bar.start()

        if label in self.tasks:
            self.progress_bar.update(self.tasks[label], completed=abs_value)
            self.progress_bar.refresh()

    def _finish(self, label: str):
        if self.progress_bar is None:
            return
        if label in self.tasks:
            self.progress_bar.update(self.tasks[label], completed=1.0)
            self.progress_bar.refresh()
            self.tasks.pop(label)
        if not self.tasks:
            self.progress_bar.stop()
            self.progress_bar = None

    def pprint(self, s: str):
        if len(s.strip("\n")) == 0:
            return None
        try:
            obj = json.loads(s, cls=CustomDecoder)

            if isinstance(
                obj, ConfigMessage
            ):  # Config messages are printed in the usual way
                errors = obj.errors
                warnings = obj.warnings
                if errors:
                    print_error_warning_table("Errors", errors)
                if warnings:
                    print_error_warning_table("Warnings", warnings)

            elif isinstance(obj, StringMessage):
                msg = obj.message
                rich.print(f"[bold]Message:[/bold] {msg}")

            elif isinstance(obj, ErrorMessage):
                msg = obj.message
                error_type = obj.error_type
                if error_type is not None:
                    rich.print(f"[red]Error ({error_type}): {msg}")
                else:
                    rich.print(f"[red]Error: {msg}")

            elif isinstance(obj, ProgressMessage):
                abs_value = obj.abs_progress
                label = obj.label
                color = obj.color
                self._update_progress(abs_value, label, color)
                if obj.finished:
                    self._finish(label)

        except json.decoder.JSONDecodeError:  # TODO: Remove this
            # TODO: This is temporary (and hacky :)
            if "status_code" in s:
                rest = (
                    "{"
                    + s.strip("status_code=0 ").replace("=", ":").replace("'", '"')
                    + "}"
                )
                print(rest)
            else:
                print(f"Error parsing message from emulator. Message is: '{s}'")


def rich_optimizer(optimizer_history: dict) -> Panel:
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("[magenta]Step", style="magenta", width=5)
    table.add_column("[cyan]Loss", style="cyan", width=18, justify="right")
    table.add_column(f"Fidelity (product)", style="white", justify="right")

    for i, step in enumerate(optimizer_history):
        table.add_row(
            str(i),
            f"{step.get('loss', np.nan):.14f}",
            f"{step.get('fidelity_product', np.nan):.14f}",
        )

    title_str = "Optimizer history"
    params_summary = (
        Text("Optimized params:", style="green"),
        Pretty(
            optimizer_history[-1]["params"],
            expand_all=True,
            indent_guides=True,
            indent_size=2,
        ),
        Text("", style="white"),  # Empty line
        Text("Final expectation value:", style="green"),
        Pretty(
            optimizer_history[-1]["loss"],
        ),
    )
    return Panel(
        Group(table, *params_summary),
        expand=False,
        title=f"[green][b]Output - {title_str}",
        border_style=INNER_GRAY,
    )


def rich_amplitudes(
    amplitudes: dict, metadata: dict[str, dict[str, Any]], noise: bool = False
) -> Panel:
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column(
        "[deep_sky_blue1]Basis state",
        justify="right",
        style="deep_sky_blue1",
        no_wrap=True,
    )
    amp_string = "Probability" if noise else "Amplitude"
    table.add_column("[magenta]Probability", style="magenta", width=20)
    table.add_column("", style="magenta")
    table.add_column(f"[cyan]{amp_string}", style="cyan")

    for basis_state, amplitude in amplitudes.items():
        if noise:
            abs_v = amplitude
        else:
            abs_v = np.real(amplitude**2)
        bar_length = int(np.round(abs_v * 20))
        table.add_row(
            basis_state,
            "▇" * bar_length,
            str(np.round(abs_v, 5)),
            str(np.round(amplitude, 5)),
        )
    title_str = "Probabilities" if noise else "Amplitudes"
    output_time = (
        metadata.get("output_metadata", {})
        .get("amplitudes", {})
        .get("time_taken", None)
    )
    subtitle_str = f"{output_time} seconds" if output_time else None
    return Panel(
        table,
        expand=False,
        title=f"[green][b]Output - {title_str}",
        subtitle=subtitle_str,
        border_style=INNER_GRAY,
    )


def rich_trajectories(trajectories: dict[str, dict]) -> Panel:
    try:
        traj_probabilities = trajectories["probabilities"]
        registers = trajectories["registers"]
    except KeyError:
        return Panel(
            Text(
                "Could not find trajectories in output data",
                style="red",
            ),
            title=f"[green][b]Trajectories",
        )

    table = Table(box=box.SIMPLE_HEAD)
    table.add_column(
        "[deep_sky_blue1]Basis state",
        justify="right",
        style="deep_sky_blue1",
        no_wrap=True,
    )
    for register_name, register_size in registers.items():
        table.add_column(
            f"[magenta]{register_name}",
            style="magenta",
            width=max(register_size, len(register_name)),
        )
    table.add_column("[cyan]Probability", style="cyan")

    traj_items: list[tuple[str, int]] | ItemsView[str, int] = traj_probabilities.items()
    MAX_NUM_TRAJ_TABLE = 20
    if len(traj_probabilities) > MAX_NUM_TRAJ_TABLE:
        traj_items = sorted(traj_items, key=lambda item: item[1], reverse=True)[
            :MAX_NUM_TRAJ_TABLE
        ]
        extra_info = f"(most relevant {MAX_NUM_TRAJ_TABLE} basis states shown)"
    else:
        extra_info = ""

    for traj_binary_repr, probability in traj_items:
        # Each key is of the form "<basis_state> <reg n> ... <reg 0>" with
        # <reg i> the i-th classical register's value in binary format
        basis_state, *registers_binary_repr = traj_binary_repr.split(" ")
        table.add_row(
            basis_state,
            *registers_binary_repr,
            str(np.round(probability, 4)),
        )

    subtitle_str = f"Total probability: {sum(traj_probabilities.values()):.7f}"
    return Panel(
        table,
        expand=False,
        title=f"[green][b]Trajectories {extra_info}",
        subtitle=subtitle_str,
        border_style=INNER_GRAY,
    )


def rich_samples(samples: dict[str, int], metadata: dict[str, dict[str, Any]]) -> Panel:
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column(
        "[deep_sky_blue1]Basis state",
        justify="right",
        style="deep_sky_blue1",
        no_wrap=True,
    )
    table.add_column("[magenta]Frequency", style="magenta", width=20)
    table.add_column("[cyan]Inferred probability", style="cyan")

    total_count = sum(c for c in samples.values())

    samples_items: list[tuple[str, int]] | ItemsView[str, int] = samples.items()
    MAX_NUM_SAMPLES_TABLE = 20
    if len(samples) > MAX_NUM_SAMPLES_TABLE:
        samples_items = sorted(samples_items, key=lambda item: item[1], reverse=True)[
            :MAX_NUM_SAMPLES_TABLE
        ]
        extra_info = f"(most relevant {MAX_NUM_SAMPLES_TABLE} basis states shown)"
    else:
        extra_info = ""

    for basis_state, count in samples_items:
        table.add_row(
            basis_state,
            str(count),
            str(np.round(count / total_count, 2)),
        )

    output_time = (
        metadata.get("output_metadata", {}).get("samples", {}).get("time_taken", None)
    )
    subtitle_str = f"{output_time} seconds" if output_time else None
    return Panel(
        table,
        expand=False,
        title=f"[green][b]Output - {total_count} samples {extra_info}",
        subtitle=subtitle_str,
        border_style=INNER_GRAY,
    )


def rich_expectations(
    expectation_values: list[dict[str, str]], metadata: dict[str, dict[str, Any]]
) -> Panel:
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column(
        "[deep_sky_blue1]Observable",
        justify="right",
        style="deep_sky_blue1",
        no_wrap=True,
    )
    table.add_column("[magenta]Expectation Value", style="magenta", width=20)
    for exp_val in expectation_values:
        value_to_print = exp_val["expval"]
        if isinstance(value_to_print, complex):
            str_val = (
                f"{round(value_to_print.real, 5)} + {round(value_to_print.imag, 5)}j"
            )
        elif isinstance(value_to_print, float):
            str_val = str(round(value_to_print, 5))
        else:
            str_val = str(value_to_print)

        table.add_row(str(exp_val["name"]), str_val)
    output_time = (
        metadata.get("output_metadata", {})
        .get("expectation_values", {})
        .get("time_taken", None)
    )
    subtitle_str = f"{output_time} seconds" if output_time else None
    return Panel(
        table,
        expand=False,
        title="[green][b]Output - Expectation Values",
        subtitle=subtitle_str,
        border_style=INNER_GRAY,
    )


def rich_mps(mps: list) -> Panel:
    # Make a string version of the mps
    tensors = [np.asarray(t) for _, t in mps]
    group_sizes = [len(t.shape) - 2 for t in tensors]
    top = "●" * group_sizes[0]
    mid = "|" * group_sizes[0]
    bot = "".join([str(d) for d in tensors[0].shape[1:-1]])
    for t, group_size in zip(tensors[1:], group_sizes[1:]):
        top_addition = f" - {t.shape[0]} - " + "●" * group_size
        top += top_addition
        mid += " " * (len(top_addition) - group_size) + "|" * group_size
        bot += " " * (len(top_addition) - group_size) + "".join(
            [str(d) for d in t.shape[1:-1]]
        )
    mps_str = Text(top + "\n" + mid + "\n" + bot, no_wrap=True, overflow="ellipsis")

    # Add extra information
    mps_len_str = f"Length: {len(mps)}"
    max_bd_str = (
        f"Max bond dimension: {max([max(t.shape[0], t.shape[-1]) for t in tensors])}\n"
    )

    group = Group(mps_len_str, max_bd_str, mps_str)
    return Panel(
        group,
        expand=False,
        title="[green][b]Output - MPS",
        border_style=INNER_GRAY,
        highlight=True,
    )


def rich_metadata(metadata: dict, config: dict) -> Panel:
    table = Table(box=box.SIMPLE_HEAD, show_header=False)
    table.add_column("", style="cyan")
    table.add_column("", style="white")

    status = metadata.get("status", None)
    if status:
        if status == "Completed":
            table.add_row("Status", "[bold green]Completed")
        else:
            table.add_row("Status", f"[bold red]{status}")

    # Number of qubits
    qubits = config.get("qubits", None)
    if qubits:
        n_qubits = len(qubits)
        table.add_row("Number of qubits", str(n_qubits))

    # Relevant bond dimension
    mode = config.get("mode")
    if mode == "dmrg":
        bond_dim = config["dmrg"]["D"]
    elif mode == "tebd":
        bond_dim = config["tebd"]["max_D"]
    elif mode == "statevector":
        bond_dim = "-"
    if mode:
        table.add_row("Mode", str(mode))
        table.add_row("Bond dimension", str(bond_dim))

    # Runtime
    runtime = metadata.get("runtime", None)
    if runtime:
        table.add_row("Runtime", str(runtime))

    # Circuit depth
    circuit_depth = metadata.get("circuit_depth", None)
    if circuit_depth:
        table.add_row("Circuit depth", str(circuit_depth))

    # Number of 2-qubit gates
    number_2qubit_gates = metadata.get("number_2qubit_gates", None)
    if number_2qubit_gates:
        table.add_row("Number of 2-qubit gates", str(number_2qubit_gates))

    # Fidelity
    fidelity = metadata.get("fidelity_product", None)
    if fidelity:
        table.add_row("Estimated fidelity", str(fidelity))

    # Gate fidelity
    gate_fidelity = metadata.get("extrapolated_2qubit_gate_fidelity", None)
    if gate_fidelity:
        table.add_row("Estimated 2-qubit gate fidelity", str(gate_fidelity))

    return Panel(table, expand=False, title="[yellow][b]Info", border_style=INNER_GRAY)


def rich_global_metadata(metadata: dict, label: str | None) -> Panel:
    table = Table(box=box.SIMPLE_HEAD, show_header=False)
    table.add_column("", style="cyan")
    table.add_column("", style="white")

    # Label
    if label is not None:
        table.add_row("Job label", label)

    # Runtime
    runtime = metadata.get("total_runtime", None)
    if runtime is not None:
        table.add_row("Total runtime (all emulations)", str(runtime))

    # Number of runs
    total_runs = metadata.get("total_runs", None)
    if total_runs is not None:
        table.add_row("Total number of emulations", str(total_runs))

    # GPU usage
    gpu_used = metadata.get("gpu_used", None)
    if gpu_used is not None:
        table.add_row("GPU-accelerated", str(gpu_used))

    # Version
    qcsim_version = metadata.get("qcsim_version", None)
    if qcsim_version is not None:
        table.add_row("Emulator version", str(qcsim_version))

    return Panel(
        table, expand=False, title="[yellow][b]Metadata", border_style=OUTER_GRAY
    )
