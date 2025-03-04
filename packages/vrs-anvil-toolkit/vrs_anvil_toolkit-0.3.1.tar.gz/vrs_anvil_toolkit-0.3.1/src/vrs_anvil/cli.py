import os
from datetime import datetime

import click
import yaml
import logging

from vrs_anvil import (
    Manifest,
    run_command_in_background,
    get_process_info,
    save_manifest,
)
from vrs_anvil.annotator import annotate_all
from logging.handlers import RotatingFileHandler
import pathlib

# Set up logging
log_format = "%(asctime)s %(threadName)s %(name)s [%(levelname)s] %(message)s"

_logger = logging.getLogger("vrs_anvil.cli")


@click.group(invoke_without_command=True)
@click.version_option(package_name="vrs_anvil_toolkit")
@click.option(
    "--manifest",
    type=click.Path(exists=False),
    default="manifest.yaml",
    help="Path to manifest file.",
)
@click.option("--verbose", default=False, help="Log more information", is_flag=True)
@click.option("--max_errors", default=10, help="Number of acceptable errors.")
@click.option(
    "--suffix", default=None, help="Substitute timestamp with alternate file suffix"
)
@click.pass_context
def cli(ctx, verbose: bool, manifest: str, max_errors: int, suffix: str):
    """GA4GH GKS utility for AnVIL."""

    _log_level = logging.INFO
    if verbose:
        _log_level = logging.DEBUG

    if suffix is not None:
        timestamp_str = suffix
    else:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with open(manifest, "r") as stream:
            manifest = Manifest.model_validate(yaml.safe_load(stream))

            # only create a persistent log for annotate subcommand
            if ctx.invoked_subcommand == "annotate":

                # Create a rotating file handler with a max size of 10MB and keep 3 backup files
                log_path = (
                    pathlib.Path(manifest.state_directory)
                    / f"vrs_anvil_{timestamp_str}.log"
                )
                file_handler = RotatingFileHandler(
                    log_path, maxBytes=10 * 1024 * 1024, backupCount=3
                )
                file_handler.setLevel(_log_level)
                file_handler.setFormatter(logging.Formatter(log_format))

                # Add the file handler to the logger
                # logger.addHandler(file_handler)
                # basicConfig call removed, which prevents the default configuration that logs to the console.
                logging.basicConfig(
                    level=_log_level, format=log_format, handlers=[file_handler]
                )

                click.secho(
                    f"🪵  Logging to {log_path}, level {logging.getLevelName(_log_level)}",
                    fg="yellow",
                )

            else:
                logging.basicConfig(level=_log_level, format=log_format)

            ctx.ensure_object(dict)
            ctx.obj["manifest"] = manifest
            ctx.obj["verbose"] = verbose
            ctx.obj["max_errors"] = max_errors
            ctx.obj["timestamp_str"] = timestamp_str

            if verbose:
                click.secho(f"📢  {manifest}", fg="green")
    except Exception as exc:
        click.secho(f"{exc}", fg="yellow")
        ctx.ensure_object(dict)


@cli.command("annotate")
@click.option(
    "--scatter",
    help="Start a background process per VCF file.",
    required=False,
    default=False,
    is_flag=True,
    show_default=True,
)
@click.pass_context
def annotate_cli(ctx, scatter: bool):
    """Read manifest file, annotate variants, all parameters controlled by manifest.yaml."""

    assert "manifest" in ctx.obj, "Manifest not found."
    timestamp_str = ctx.obj["timestamp_str"]

    # normal run with single process
    if not scatter:
        try:
            manifest = ctx.obj["manifest"]
            manifest_path = f"{manifest.work_directory}/manifest_{timestamp_str}.yaml"
            save_manifest(manifest, manifest_path)
            click.secho(f"🔑 Manifest saved at {manifest_path}", fg="yellow")
            _logger.debug(f"Manifest: {ctx.obj['manifest']}")

            click.secho("🚧  annotating variants", fg="yellow")
            metrics_file = annotate_all(
                manifest, max_errors=ctx.obj["max_errors"], timestamp_str=timestamp_str
            )
            click.secho(f"📊  metrics available in {metrics_file}", fg="green")
        except Exception as exc:
            click.secho(f"{exc}", fg="red")
            _logger.exception(exc)
    else:  # scattered processes / multiprocessing
        try:
            parent_manifest = ctx.obj["manifest"]
            scattered_processes = []
            child_processes = []

            for i, vcf_file in enumerate(parent_manifest.vcf_files):
                # create a new manifest for each VCF file based on the parent manifest
                child_manifest = parent_manifest.copy(deep=True)
                child_manifest.vcf_files = [vcf_file]
                child_manifest.num_threads = 1
                child_manifest.disable_progress_bars = True

                suffix_str = f"scattered_{timestamp_str}_{i}"
                child_manifest_path = (
                    pathlib.Path(child_manifest.work_directory)
                    / f"manifest_{suffix_str}.yaml"
                )
                save_manifest(child_manifest, child_manifest_path)
                click.secho(f"🔑 Manifest saved at {child_manifest_path}", fg="yellow")
                _logger.debug(f"Manifest: {ctx.obj['manifest']}")

                # run process to annotate each manifest
                process = run_command_in_background(
                    f"vrs_bulk --manifest {child_manifest_path} --suffix {suffix_str} annotate"
                )
                click.secho(
                    f"🚧  annotating {vcf_file} on pid {process.pid}", fg="yellow"
                )
                scattered_processes.append(
                    {
                        "pid": process.pid,
                        "manifest": str(child_manifest_path),
                        "vcf": vcf_file,
                    }
                )
                child_processes.append(process)

            # associate scattered processes to process id in yaml
            scattered_processes_path = (
                pathlib.Path(parent_manifest.work_directory)
                / f"scattered_processes_{timestamp_str}.yaml"
            )
            scattered_processes = {
                "parent_pid": os.getpid(),
                "processes": scattered_processes,
            }
            with open(scattered_processes_path, "w") as stream:
                yaml.dump(scattered_processes, stream)
            click.secho(
                f"📊 scattered processes available in {scattered_processes_path}",
                fg="green",
            )

            # ensure all processes completed
            click.secho("🕒 waiting for processes to complete", fg="yellow")
            try:
                for process in child_processes:
                    process.wait()
            except KeyboardInterrupt:
                click.secho(
                    "🚨 caught KeyboardInterrupt, terminating child processes",
                    fg="red",
                )
                for process in child_processes:
                    process.terminate()
                for process in child_processes:
                    process.wait()

            click.secho("✅  all processes completed", fg="green")
        except Exception as exc:
            click.secho(f"{exc}", fg="red")
            _logger.exception(exc)


# TODO: allow user to pass in a particular timestamp?
@cli.command("ps")
@click.pass_context
def ps_cli(ctx):
    """Show status of latest scatter command."""

    try:
        assert "manifest" in ctx.obj, "Manifest not found."
        parent_manifest = ctx.obj["manifest"]

        # get most recent set of scattered manifests
        file_prefix = "scattered_processes_"
        filename_match = f"{file_prefix}*.yaml"

        scattered_processes_path = pathlib.Path(parent_manifest.work_directory)
        scattered_processes_paths = sorted(
            x for x in scattered_processes_path.glob(filename_match)
        )
        if not scattered_processes_paths:
            click.secho(
                f"🚧  no scattered processes found in {parent_manifest.work_directory}/{filename_match}",
                fg="red",
            )
            return
        scattered_processes_path = scattered_processes_paths[-1]

        # list associated info for each process
        state_dir = pathlib.Path(parent_manifest.state_directory)
        with open(scattered_processes_path, "r") as stream:
            scattered_processes = yaml.safe_load(stream)
            for process in scattered_processes["processes"]:
                manifest_path = process["manifest"]
                timestamp_str = (
                    str(manifest_path).split("manifest_scattered_")[1].split(".")[0]
                )

                log_file = "NA"
                metrics_file = "NA"

                try:
                    log_file = list(state_dir.glob(f"vrs_anvil_*{timestamp_str}.log"))[
                        -1
                    ]
                    metrics_file = list(
                        state_dir.glob(f"metrics_*{timestamp_str}.yaml")
                    )[-1]
                except Exception:
                    pass

                click.secho(
                    f"🚧  pid: {str(process['pid'])}, manifest: {str(process['manifest'])}, vcf: {str(process['vcf'])}, metrics_file: {metrics_file}, log_file: {log_file}",
                    fg="yellow",
                )
                process_info = get_process_info(process["pid"])
                if not process_info or metrics_file != "NA":
                    click.secho("  ✅  completed", fg="green")
                else:
                    io_counters = "NA"
                    memory_info = "NA"
                    cpu_percent = "NA"

                    status = process_info.status()
                    if status == "running":
                        try:
                            if hasattr(process_info, "io_counters"):
                                io_counters = process_info.io_counters()
                            if hasattr(process_info, "memory_info"):
                                memory_info = process_info.memory_info()
                            if hasattr(process_info, "cpu_percent"):
                                cpu_percent = process_info.cpu_percent(interval=0.1)
                        except Exception as exc:
                            _logger.info(
                                f"could not get io_counters/memory_info pid: {process['pid']} error:{exc}"
                            )

                        click.secho(
                            f"  📊 {status.capitalize()}: cpu_percent: {cpu_percent}%, io_counters: {io_counters}, memory_info: {memory_info}",
                            fg="yellow",
                        )
    except Exception as exc:
        click.secho(f"{exc}", fg="red")
        _logger.exception(exc)


if __name__ == "__main__":
    cli()
