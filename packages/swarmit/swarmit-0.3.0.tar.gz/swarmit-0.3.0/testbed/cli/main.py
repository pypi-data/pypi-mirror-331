#!/usr/bin/env python

import logging
import time

import click
import serial
import structlog
from dotbot.serial_interface import SerialInterfaceException, get_default_port
from rich import print
from rich.console import Console
from rich.pretty import pprint

from testbed.swarmit import __version__
from testbed.swarmit.controller import (
    CHUNK_SIZE,
    Controller,
    ControllerSettings,
    ResetLocation,
    print_start_status,
    print_status,
    print_stop_status,
    print_transfer_status,
)

SERIAL_PORT_DEFAULT = get_default_port()
BAUDRATE_DEFAULT = 1000000


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__)
@click.option(
    "-p",
    "--port",
    default=SERIAL_PORT_DEFAULT,
    help=f"Serial port to use to send the bitstream to the gateway. Default: {SERIAL_PORT_DEFAULT}.",
)
@click.option(
    "-b",
    "--baudrate",
    default=BAUDRATE_DEFAULT,
    help=f"Serial port baudrate. Default: {BAUDRATE_DEFAULT}.",
)
@click.option(
    "-e",
    "--edge",
    is_flag=True,
    default=False,
    help="Use MQTT adapter to communicate with an edge gateway.",
)
@click.option(
    "-d",
    "--devices",
    type=str,
    default="",
    help="Subset list of devices to interact with, separated with ,",
)
@click.pass_context
def main(ctx, port, baudrate, edge, devices):
    if ctx.invoked_subcommand != "monitor":
        # Disable logging if not monitoring
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(
                logging.CRITICAL
            ),
        )
    ctx.ensure_object(dict)
    ctx.obj["port"] = port
    ctx.obj["baudrate"] = baudrate
    ctx.obj["edge"] = edge
    ctx.obj["devices"] = [e for e in devices.split(",") if e]


@main.command()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Print start result.",
)
@click.pass_context
def start(ctx, verbose):
    """Start the user application."""
    try:
        settings = ControllerSettings(
            serial_port=ctx.obj["port"],
            serial_baudrate=ctx.obj["baudrate"],
            mqtt_host="argus.paris.inria.fr",
            mqtt_port=8883,
            edge=ctx.obj["edge"],
            devices=list(ctx.obj["devices"]),
        )
        controller = Controller(settings)
    except (
        SerialInterfaceException,
        serial.serialutil.SerialException,
    ) as exc:
        console = Console()
        console.print(f"[bold red]Error:[/] {exc}")
        return
    if controller.ready_devices:
        started = controller.start()
        print_start_status(
            sorted(started),
            sorted(set(controller.ready_devices).difference(set(started))),
        )
        if verbose:
            print("Started devices:")
            pprint(started)
            print("Not started devices:")
            pprint(
                sorted(set(controller.ready_devices).difference(set(started)))
            )
    else:
        print("No device to start")
    controller.terminate()


@main.command()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Print start result.",
)
@click.pass_context
def stop(ctx, verbose):
    """Stop the user application."""
    try:
        settings = ControllerSettings(
            serial_port=ctx.obj["port"],
            serial_baudrate=ctx.obj["baudrate"],
            mqtt_host="argus.paris.inria.fr",
            mqtt_port=8883,
            edge=ctx.obj["edge"],
            devices=list(ctx.obj["devices"]),
        )
        controller = Controller(settings)
    except (
        SerialInterfaceException,
        serial.serialutil.SerialException,
    ) as exc:
        console = Console()
        console.print(f"[bold red]Error:[/] {exc}")
        return
    if controller.running_devices or controller.resetting_devices:
        stopped = controller.stop()
        print_stop_status(
            sorted(stopped),
            sorted(
                set(
                    controller.running_devices + controller.resetting_devices
                ).difference(set(stopped))
            ),
        )
        if verbose:
            print("Started devices:")
            pprint(stopped)
            print("Not started devices:")
            pprint(
                sorted(
                    set(
                        controller.running_devices
                        + controller.resetting_devices
                    ).difference(set(stopped))
                )
            )
    else:
        print("No device to stop")
    controller.terminate()


@main.command()
@click.argument(
    "locations",
    type=str,
)
@click.pass_context
def reset(ctx, locations):
    """Reset robots locations.

    Locations are provided as '<device_id>:<x>,<y>-<device_id>:<x>,<y>|...'
    """
    devices = ctx.obj["devices"]
    if not devices:
        print("No devices selected.")
        return
    locations = {
        location.split(':')[0]: ResetLocation(
            pos_x=int(float(location.split(':')[1].split(',')[0]) * 1e6),
            pos_y=int(float(location.split(':')[1].split(',')[1]) * 1e6),
        )
        for location in locations.split("-")
    }
    if sorted(devices) and sorted(locations.keys()) != sorted(devices):
        print("Selected devices and reset locations do not match.")
        return
    try:
        settings = ControllerSettings(
            serial_port=ctx.obj["port"],
            serial_baudrate=ctx.obj["baudrate"],
            mqtt_host="argus.paris.inria.fr",
            mqtt_port=8883,
            edge=ctx.obj["edge"],
            devices=list(ctx.obj["devices"]),
        )
        controller = Controller(settings)
    except (
        SerialInterfaceException,
        serial.serialutil.SerialException,
    ) as exc:
        console = Console()
        console.print(f"[bold red]Error:[/] {exc}")
        return
    if not controller.ready_devices:
        print("No device to reset.")
        return
    controller.reset(locations)
    controller.terminate()


@main.command()
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flash the firmware without prompt.",
)
@click.option(
    "-s",
    "--start",
    is_flag=True,
    help="Start the firmware once flashed.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Print transfer data.",
)
@click.argument("firmware", type=click.File(mode="rb"), required=False)
@click.pass_context
def flash(ctx, yes, start, verbose, firmware):
    """Flash a firmware to the robots."""
    console = Console()
    if firmware is None:
        console.print("[bold red]Error:[/] Missing firmware file. Exiting.")
        ctx.exit()

    fw = bytearray(firmware.read())
    settings = ControllerSettings(
        serial_port=ctx.obj["port"],
        serial_baudrate=ctx.obj["baudrate"],
        mqtt_host="argus.paris.inria.fr",
        mqtt_port=8883,
        edge=ctx.obj["edge"],
        devices=ctx.obj["devices"],
    )
    controller = Controller(settings)
    if not controller.ready_devices:
        console.print("[bold red]Error:[/] No ready devices found. Exiting.")
        controller.terminate()
        return
    print(
        f"Devices to flash ([bold white]{len(controller.ready_devices)}):[/]"
    )
    pprint(controller.ready_devices, expand_all=True)
    if yes is False:
        click.confirm("Do you want to continue?", default=True, abort=True)

    devices = controller.settings.devices
    start_data = controller.start_ota(fw)
    if (devices and sorted(start_data.ids) != sorted(devices)) or (
        not devices
        and sorted(start_data.ids) != sorted(controller.ready_devices)
    ):
        console = Console()
        console.print(
            "[bold red]Error:[/] some acknowledgments are missing "
            f'({", ".join(sorted(set(controller.ready_devices).difference(set(start_data.ids))))}). '
            "Aborting."
        )
        raise click.Abort()
    print()
    print(f"Image size: [bold cyan]{len(fw)}B[/]")
    print(f"Image hash: [bold cyan]{start_data.fw_hash.hex().upper()}[/]")
    print(f"Radio chunks ([bold]{CHUNK_SIZE}B[/bold]): {start_data.chunks}")
    start_time = time.time()
    data = controller.transfer(fw)
    print(f"Elapsed: [bold cyan]{time.time() - start_time:.3f}s[/bold cyan]")
    print_transfer_status(data, start_data)
    if verbose:
        pprint(data)
    if not all([value.hashes_match for value in data.values()]):
        controller.terminate()
        console = Console()
        console.print("[bold red]Error:[/] Hashes do not match.")
        raise click.Abort()

    if start is True:
        started = controller.start()
        print_start_status(
            sorted(started),
            sorted(set(start_data.ids).difference(set(started))),
        )
    controller.terminate()


@main.command()
@click.pass_context
def monitor(ctx):
    """Monitor running applications."""
    try:
        settings = ControllerSettings(
            serial_port=ctx.obj["port"],
            serial_baudrate=ctx.obj["baudrate"],
            mqtt_host="argus.paris.inria.fr",
            mqtt_port=8883,
            edge=ctx.obj["edge"],
            devices=ctx.obj["devices"],
        )
        controller = Controller(settings)
    except (
        SerialInterfaceException,
        serial.serialutil.SerialException,
    ) as exc:
        console = Console()
        console.print(f"[bold red]Error:[/] {exc}")
        return {}
    try:
        controller.monitor()
    except KeyboardInterrupt:
        print("Stopping monitor.")
    finally:
        controller.terminate()


@main.command()
@click.pass_context
def status(ctx):
    """Print current status of the robots."""
    settings = ControllerSettings(
        serial_port=ctx.obj["port"],
        serial_baudrate=ctx.obj["baudrate"],
        mqtt_host="argus.paris.inria.fr",
        mqtt_port=8883,
        edge=ctx.obj["edge"],
        devices=ctx.obj["devices"],
    )
    controller = Controller(settings)
    data = controller.status()
    if not data:
        click.echo("No devices found.")
    else:
        print_status(data)
    controller.terminate()


@main.command()
@click.argument("message", type=str, required=True)
@click.pass_context
def message(ctx, message):
    """Send a custom text message to the robots."""
    settings = ControllerSettings(
        serial_port=ctx.obj["port"],
        serial_baudrate=ctx.obj["baudrate"],
        mqtt_host="argus.paris.inria.fr",
        mqtt_port=8883,
        edge=ctx.obj["edge"],
        devices=ctx.obj["devices"],
    )
    controller = Controller(settings)
    controller.send_message(message)
    controller.terminate()


if __name__ == "__main__":
    main(obj={})
