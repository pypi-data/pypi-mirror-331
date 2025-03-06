from pathlib import Path
from typing import Callable, Optional, Union

import qcparse
from qcio import CalcType, ProgramInput, ProgramOutput, SinglePointResults
from qcparse import exceptions as qcparse_exceptions
from qcparse.encoders.terachem import XYZ_FILENAME
from qcparse.parsers.terachem import parse_optimization_dir, parse_version_string

from qcop.exceptions import AdapterError, AdapterInputError, ExternalProgramError

from .base import ProgramAdapter
from .utils import execute_subprocess


class TeraChemAdapter(ProgramAdapter[ProgramInput, SinglePointResults]):
    """Adapter for TeraChem."""

    supported_calctypes = [
        CalcType.energy,
        CalcType.gradient,
        CalcType.hessian,
        CalcType.optimization,
    ]
    """Supported calculation types."""
    program = "terachem"

    def program_version(self, stdout: Optional[str] = None) -> str:
        """Get the program version.

        Args:
            stdout: The stdout from the program.

        Returns:
            The program version.
        """
        if stdout:
            try:
                return parse_version_string(stdout)
            except qcparse_exceptions.ParserError:
                # If the version string is not found. Happens when libcuda.so is not
                # found and TeraChem fails to start. terachem --version will fail too.
                return "Could not parse version"
        else:
            try:
                return execute_subprocess(self.program, ["--version"])[17:]
            except ExternalProgramError:
                return "Could not determine version"

    # TODO: Need command line options for TeraChem e.g., -g 1 for GPUs MAYBE?
    # Try using it for a while without and see what roadblocks we run into
    def compute_results(
        self,
        inp_obj: ProgramInput,
        update_func: Optional[Callable] = None,
        update_interval: Optional[float] = None,
        **kwargs,
    ) -> tuple[SinglePointResults, str]:
        """Execute TeraChem on the given input.

        Args:
            inp_obj: The qcio ProgramInput object for a computation.
            update_func: A callback function to call as the program executes.
            update_interval: The minimum time in seconds between calls to the
                update_func.

        Returns:
            A tuple of SinglePointResults and the stdout str.
        """
        # Construct and write input file and xyz file to disk
        try:
            native_input = qcparse.encode(inp_obj, self.program)
        except qcparse.exceptions.EncoderError as e:
            raise AdapterInputError(program=self.program) from e

        input_filename = "tc.in"
        Path(input_filename).write_text(native_input.input_file)
        Path(native_input.geometry_filename).write_text(native_input.geometry_file)

        # Execute TeraChem
        stdout = execute_subprocess(
            self.program, [input_filename], update_func, update_interval
        )

        # Parse output
        try:
            if inp_obj.calctype == CalcType.optimization:
                parsed_output = parse_optimization_dir(
                    f"scr.{XYZ_FILENAME.split('.')[0]}", stdout, inp_obj=inp_obj
                )
            else:
                parsed_output = qcparse.parse(stdout, self.program, "stdout")
        except qcparse_exceptions.ParserError as e:
            raise ExternalProgramError(
                program="qcparse",
                message="Failed to parse TeraChem output.",
                stdout=stdout,
                original_exception=e,
            ) from e
        return parsed_output, stdout

    def collect_wfn(self) -> dict[str, Union[str, bytes]]:
        """Append wavefunction data to the output."""

        # Naming conventions from TeraChem uses xyz filename as scratch dir postfix
        scr_postfix = XYZ_FILENAME.split(".")[0]

        # Wavefunction filenames
        wfn_filenames = ("c0", "ca0", "cb0")
        wfn_paths = [Path(f"scr.{scr_postfix}/{fn}") for fn in wfn_filenames]
        if not any(wfn_path.exists() for wfn_path in wfn_paths):
            raise AdapterError(f"No wavefunction files found in {Path.cwd()}")

        wfns: dict[str, Union[str, bytes]] = {}
        for wfn_path in wfn_paths:
            if wfn_path.exists():
                wfns[str(wfn_path)] = wfn_path.read_bytes()
        return wfns

    def propagate_wfn(self, output: ProgramOutput, prog_inp: ProgramInput) -> None:
        """Propagate the wavefunction from the previous calculation.

        Args:
            output: The output from a previous calculation containing wavefunction data.
            prog_inp: The ProgramInput object on which to place the wavefunction data.

        Returns:
            None. Modifies the prog_inp object in place.
        """

        # Naming conventions from TeraChem uses xyz filename as scratch dir postfix
        scr_postfix = XYZ_FILENAME.split(".")[0]

        # Wavefunction filenames
        c0, ca0, cb0 = "c0", "ca0", "cb0"

        c0_bytes = output.results.files.get(f"scr.{scr_postfix}/{c0}")
        ca0_bytes = output.results.files.get(f"scr.{scr_postfix}/{ca0}")
        cb0_bytes = output.results.files.get(f"scr.{scr_postfix}/{cb0}")

        if not c0_bytes and not (ca0_bytes and cb0_bytes):
            raise AdapterInputError(
                program=self.program,
                message="Could not find c0 or ca/b0 files in output.",
            )

        # Load wavefunction data onto ProgramInput object

        if c0_bytes:
            prog_inp.files[c0] = c0_bytes
            prog_inp.keywords["guess"] = c0

        else:  # ca0_bytes and cb0_bytes
            assert ca0_bytes and cb0_bytes  # for mypy
            prog_inp.files[ca0] = ca0_bytes
            prog_inp.files[cb0] = cb0_bytes
            prog_inp.keywords["guess"] = f"{ca0} {cb0}"
