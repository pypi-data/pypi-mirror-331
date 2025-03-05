"""CLI command to generate an HTML report from ECLYPSE simulation report stats."""

from pathlib import Path
from typing import Tuple

import click

from .report import HTMLReport


@click.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--range",
    "-r",
    "report_range",
    type=(int, int),
    default=(0, int(1e9)),
    help="Range to report, as a tuple (start, end). [default: (0, MAX_FLOAT)]",
)
@click.option(
    "--step",
    "-s",
    "report_step",
    type=int,
    default=1,
    show_default=True,
    help="Step to report.",
)
@click.option(
    "--open",
    "-o",
    "open_html",
    is_flag=True,
    default=False,
    show_default=True,
    help="Flag to open the generated report in the browser.",
)
@click.option(
    "--force-reload",
    "-f",
    "force_reload",
    is_flag=True,
    default=False,
    show_default=True,
    help="Flag to force reload the stats from the simulation, even if a 'report.html' already exists.",
)
def main(
    input_path: Path,
    report_range: Tuple[int, int],
    report_step: int,
    open_html: bool,
    force_reload: bool,
):
    """CLI tool to generate an HTML report from ECLYPSE simulation report stats.

    INPUT_PATH: Required path to the report stats.
    """

    exists = (input_path / "report.html").exists()

    if exists and not force_reload:
        click.secho(
            "\nReport already exists. Use --force-reload/-f to force reload.",
            err=True,
            fg="red",
            bold=True,
        )
        return

    if exists and force_reload:
        click.secho("\nReloading stats", fg="yellow", bold=True)

    report = HTMLReport(simulation_path=input_path)
    report.load_stats(report_range=report_range, report_step=report_step)
    report.to_html(open_html=open_html)
