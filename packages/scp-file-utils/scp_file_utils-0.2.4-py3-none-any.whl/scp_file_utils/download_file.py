import os
from datetime import datetime
import subprocess

import os
import sys
import click
import pathlib
import json
import logging
import calendar
import time
import pathlib
import yaml

from datetime import datetime
from rich.console import Console
from typing import Any, Dict

from scp_file_utils import constants
from scp_file_utils.file_utils import check_infile_status


error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.basename(__file__),
    constants.DEFAULT_TIMESTAMP,
)


# DOWNLOADS_DIR = "C:\\Users\\jps0428\\Downloads"
DOWNLOADS_DIR = constants.DEFAULT_DOWNLOADS_DIR


def create_directory(path):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_current_user():
    """Returns the current user identifier."""
    return os.getlogin()


def download_file(
    config: Dict[str, Any],
    logfile: str,
    outdir: str,
    outfile: str,
    verbose: bool = constants.DEFAULT_VERBOSE,
) -> None:
    """Download the file from the remote server.

    Args:
        config (Dict[str, Any]): The configuration dictionary.
        logfile (str): The log file.
        outdir (str): The output directory.
        outfile (str): The output file.
        verbose (bool): The verbosity flag.
    """
    # Prompt user for asset path
    asset_path = input("What is the path for the asset? ")

    # Prompt user for remote server
    server = input("What is the remote server? ")

    # Prompt for destination (Azure or Jira)
    azure = input("azure? [Y/n] ").lower().strip() == "y"
    if not azure:
        jira = input("jira? [Y/n] ").lower().strip() == "y"

    # Create download directory with timestamp if no target specified
    if not (azure or jira):
        current_time = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        target_dir = os.path.join(DOWNLOADS_DIR, current_time)
        create_directory(target_dir)
    else:
        # Create Downloads/azure or Downloads/jira if needed
        target_dir = os.path.join(DOWNLOADS_DIR, ("azure" if azure else "jira"))
        create_directory(target_dir)

        # Prompt for issue id based on selection
        if azure:
            issue_id = input("Azure issue id? ")
        else:
            issue_id = input("Jira issue id? ")

        # Create subdirectory within target dir for the issue
        target_dir = os.path.join(target_dir, issue_id)
        create_directory(target_dir)

    # Get current user
    user = get_current_user()

    # Construct the SCP command
    command = f"scp {user}@{server}:{asset_path} {target_dir}"

    # Execute the SCP command
    subprocess.run(command.split())

    transferred_file = os.path.join(target_dir, os.path.basename(asset_path))
    check_infile_status(transferred_file)

    print(f"The asset has been transferred to '{target_dir}'")


def validate_verbose(ctx, param, value):
    """Validate the validate option.

    Args:
        ctx (Context): The click context.
        param (str): The parameter.
        value (bool): The value.

    Returns:
        bool: The value.
    """

    if value is None:
        click.secho(
            "--verbose was not specified and therefore was set to 'True'", fg="yellow"
        )
        return constants.DEFAULT_VERBOSE
    return value


@click.command()
@click.option(
    "--config_file",
    type=click.Path(exists=True),
    help=f"The configuration file for this project - default is '{constants.DEFAULT_CONFIG_FILE}'.",
)
@click.option("--logfile", help="The log file.")
@click.option(
    "--outdir",
    help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'.",
)
@click.option("--outfile", help="The output final report file.")
@click.option(
    "--verbose",
    is_flag=True,
    help=f"Will print more info to STDOUT - default is '{constants.DEFAULT_VERBOSE}'.",
    callback=validate_verbose,
)
def main(config_file: str, logfile: str, outdir: str, outfile: str, verbose: bool):
    """Download file from remote server via scp command."""
    error_ctr = 0

    if error_ctr > 0:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if config_file is None:
        config_file = constants.DEFAULT_CONFIG_FILE
        console.print(
            f"[yellow]--config_file was not specified and therefore was set to '{config_file}'[/]"
        )

    check_infile_status(config_file, "yaml")

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        console.print(
            f"[yellow]--outdir was not specified and therefore was set to '{outdir}'[/]"
        )

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        console.print(f"[yellow]Created output directory '{outdir}'[/]")

    if logfile is None:
        logfile = os.path.join(
            outdir, os.path.splitext(os.path.basename(__file__))[0] + ".log"
        )
        console.print(
            f"[yellow]--logfile was not specified and therefore was set to '{logfile}'[/]"
        )

    logging.basicConfig(
        filename=logfile,
        format=constants.DEFAULT_LOGGING_FORMAT,
        level=constants.DEFAULT_LOGGING_LEVEL,
    )

    logging.info("Will load contents of config file 'config_file'")
    config = yaml.safe_load(pathlib.Path(config_file).read_text())

    download_file(config, logfile, outdir, outfile, verbose)

    if verbose:
        print(f"The log file is '{logfile}'")
        console.print(
            f"[bold green]Execution of '{os.path.abspath(__file__)}' completed[/]"
        )


if __name__ == "__main__":
    main()
