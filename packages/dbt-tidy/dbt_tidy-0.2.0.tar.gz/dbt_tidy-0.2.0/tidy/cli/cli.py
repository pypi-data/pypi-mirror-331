import importlib
import pkgutil
import pathlib
import sys

import click

from tidy.manifest import ManifestWrapper
from tidy.sweeps.base import CheckResult

DEFAULT_CHECKS_PATH = importlib.resources.files(importlib.import_module("tidy.sweeps"))
USER_CHECKS_PATH = pathlib.Path.cwd() / ".tidy"


def import_module_from_path(module_name, path):
    """Dynamically import a module from a given file path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_and_run_checks(manifest, check_names=None):
    results = []

    for finder, name, ispkg in pkgutil.walk_packages(
        [str(DEFAULT_CHECKS_PATH)], "tidy.sweeps."
    ):
        if ispkg:
            continue

        module = importlib.import_module(name)

        for attr_name in dir(module):
            # breakpoint()
            attr = getattr(module, attr_name)

            if callable(attr) and getattr(attr, "__is_sweep__", False):
                check_name = getattr(attr, "__sweep_name__", attr_name)

                if check_names and check_name not in check_names:
                    continue

                check_result = attr(manifest)
                if isinstance(check_result, CheckResult):
                    results.append(check_result)

    if USER_CHECKS_PATH.exists():
        sys.path.insert(0, str(USER_CHECKS_PATH))

        for check_file in USER_CHECKS_PATH.rglob("*.py"):
            module_name = (
                check_file.relative_to(USER_CHECKS_PATH)
                .with_suffix("")
                .as_posix()
                .replace("/", ".")
            )

            if check_names and module_name.split(".")[-1] not in check_names:
                continue

            module = import_module_from_path(module_name, check_file)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and getattr(attr, "__is_sweep__", False):
                    check_name = getattr(attr, "__sweep_name__", attr_name)

                    if check_names and check_name not in check_names:
                        continue

                    check_result = attr(manifest)
                    if isinstance(check_result, CheckResult):
                        results.append(check_result)

    return results


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--manifest-path",
    default="target/manifest.json",
    show_default=True,
    help="Path to the dbt manifest file.",
)
@click.option(
    "--max-details",
    "-md",
    default=5,
    show_default=True,
    help="Maximum number of details to display per result.",
)
@click.option(
    "--sweeps",
    "-s",
    multiple=True,
    help="List of check names to run. If not specified, all checks will be run.",
)
def sweep(
    manifest_path,
    max_details,
    sweeps,
):
    manifest = ManifestWrapper.load(manifest_path)

    click.secho("Sweeping...", fg="cyan", bold=True)
    results = discover_and_run_checks(manifest, sweeps)

    for result in results:
        status_color = {"pass": "green", "fail": "red", "warning": "yellow"}.get(
            result.status.value, "white"
        )

        click.secho(f"\n{result.name}", fg="cyan", bold=True)
        click.secho(f"Status: {result.status.value}", fg=status_color)

        if result.nodes:
            click.secho("Nodes:", fg="blue")
            for detail in result.nodes[:max_details]:
                click.echo(f"  - {detail}")

            if len(result.nodes) > max_details:
                click.secho(
                    f"  ...and {len(result.nodes) - max_details} more", fg="yellow"
                )


if __name__ == "__main__":
    cli()
