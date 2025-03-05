from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List

import typer

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"


OPTIONS = {}

OPTIONS["input_file"]: Path = typer.Option(
    ...,
    "-i",
    "--input-file",
    help="path to the input file.",
    exists=True,
    file_okay=True,
    readable=True,
    resolve_path=True,
)
OPTIONS["output_file"]: Path = typer.Option(
    None,
    "-o",
    "--output-file",
    help="path to the output file.",
    exists=False,
    writable=True,
)
OPTIONS["connectivity_files"]: List[Path] = typer.Option(
    ...,
    "-c",
    "--connectivity-files",
    help="path to one or more connectivity file.",
    exists=True,
    file_okay=True,
    readable=True,
    resolve_path=True,
)
OPTIONS["scan_directory"]: Path = typer.Option(
    ...,
    "-s",
    "--scan-directory",
    help="path to the input YARR scan directory.",
    exists=True,
    file_okay=True,
    readable=True,
    resolve_path=True,
)
OPTIONS["per_chip"]: bool = typer.Option(
    False, "--per-chip", help="divide summary per chip."
)
OPTIONS["config_summary"]: bool = typer.Option(
    True, "--config-summary", help="plot config summary in YARR scan."
)
OPTIONS["verbosity"]: LogLevel = typer.Option(
    LogLevel.info,
    "-v",
    "--verbosity",
    help="Log level [options: DEBUG, INFO (default) WARNING, ERROR]",
)
