#!/usr/bin/env python3
from sys import stdin
from typing import Optional

import click
from click_tree import ClickTreeParam
from fabric2.config import Config

from smn.context import Context, pass_context  # noqa: F401
from smn.runners import Local, Remote


@click.group(
    name="smn",
    context_settings={"help_option_names": ["--smn-help"]},
)
@click.option(
    "--tome",
    "_tome",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=False,
    help="directly specify path to root tome",
)
@click.option(
    "--tree",
    is_flag=True,
    type=ClickTreeParam(scoped=True, ignore_names=["smn-run"]),
    help="enable tree display",
)
@click.option("--dry-run", is_flag=True, default=False, help="enable dry-run mode")
@click.option(
    "--disable-execution",
    is_flag=True,
    default=False,
    help="disable all command execution",
)
@click.option(
    "--debug", is_flag=True, default=False, help="output additional debug info"
)
@click.option(
    "-H",
    "--host",
    type=str,
    default="local",
    help="host to run commands on via ssh, defaults to local execution",
)
@click.option(
    "--cache-force",
    is_flag=True,
    default=False,
    help="cache: force a reload of all cached commands, regardless of ttl",
)
@click.option(
    "--cache-disable",
    is_flag=True,
    default=False,
    help="cache: disable all command caching",
)
@click.pass_context
def tome(
    click_ctx: click.Context,
    _tome: Optional[str],
    tree: Optional[bool],
    dry_run: bool,
    disable_execution: bool,
    debug: bool,
    host: str,
    cache_force: bool,
    cache_disable: bool,
) -> None:
    """a macro command runner"""

    # Create our smn Context conditionally using a supplied remote host if any,
    # and set it on the current click.Context. This is more or less what the
    # ensure=True flag on make_pass_decorator does under the hood, but this allows
    # for constructing the Context with our own arguments.
    ctx = Context(host)
    click_ctx.obj = ctx

    ctx._set(smn_dry_run=dry_run)
    ctx._set(smn_debug=debug)
    ctx._set(smn_cache_force=cache_force)
    ctx._set(smn_cache_disable=cache_disable)

    cfg = {}
    cfg["run"] = {
        # Enable echo of all running commands.
        "echo": ctx.smn_debug,
        # Mirror tty configuration of environment that is invoking smn. For example,
        # echo '{}' | tee empty.json will set pty=False, which will allow stdin
        # to flow in.
        "pty": stdin.isatty(),
        # Disable all invoke command execution, this seems to also force echo=True.
        "dry": disable_execution,
    }

    # Use smn's custom Local and Remote runners for all actions.
    cfg["runners"] = {
        "local": Local,
        "remote": Remote,
    }

    ctx.config = Config(overrides=cfg)
