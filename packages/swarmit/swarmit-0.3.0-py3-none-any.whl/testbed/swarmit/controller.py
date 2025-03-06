"""Module containing the swarmit controller class."""

import dataclasses
import time
from dataclasses import dataclass
from typing import Optional

import serial
from cryptography.hazmat.primitives import hashes
from dotbot.logger import LOGGER
from dotbot.protocol import Frame, Header
from dotbot.serial_interface import SerialInterfaceException, get_default_port
from rich import print
from rich.console import Console
from rich.live import Live
from rich.table import Table
from tqdm import tqdm

from testbed.swarmit.adapter import (
    GatewayAdapterBase,
    MQTTAdapter,
    SerialAdapter,
)
from testbed.swarmit.protocol import (
    PayloadMessage,
    PayloadOTAChunkRequest,
    PayloadOTAStartRequest,
    PayloadResetRequest,
    PayloadStartRequest,
    PayloadStatusRequest,
    PayloadStopRequest,
    StatusType,
    SwarmitPayloadType,
    register_parsers,
)

CHUNK_SIZE = 128
SERIAL_PORT_DEFAULT = get_default_port()


@dataclass
class DataChunk:
    """Class that holds data chunks."""

    index: int
    size: int
    data: bytes


@dataclass
class StartOtaData:
    """Class that holds start ota data."""

    chunks: int = 0
    fw_hash: bytes = b""
    ids: list[str] = dataclasses.field(default_factory=lambda: [])


@dataclass
class TransferDataStatus:
    """Class that holds transfer data status for a single device."""

    retries: list[int] = dataclasses.field(default_factory=lambda: [])
    chunks_acked: set[int] = dataclasses.field(default_factory=lambda: set())
    hashes_match: bool = False


@dataclass
class ResetLocation:
    """Class that holds reset location."""

    pos_x: int = 0
    pos_y: int = 0

    def __repr__(self):
        return f"(x={self.pos_x}, y={self.pos_y})"


def print_status(status_data: dict[str, StatusType]) -> None:
    """Print the status of the devices."""
    print()
    print(
        f"{len(status_data)} device{'s' if len(status_data) > 1 else ''} found"
    )
    print()
    status_table = Table()
    status_table.add_column("Device ID", style="magenta", no_wrap=True)
    status_table.add_column("Status", style="green", justify="center")
    with Live(status_table, refresh_per_second=4) as live:
        live.update(status_table)
        for device_id, status in sorted(status_data.items()):
            status_table.add_row(
                f"{device_id}",
                f'{"[bold cyan]" if status == StatusType.Running else "[bold green]"}{status.name}',
            )


def print_start_status(
    stopped_data: list[str], not_started: list[str]
) -> None:
    """Print the start status."""
    print("[bold]Start status:[/]")
    status_table = Table()
    status_table.add_column("Device ID", style="magenta", no_wrap=True)
    status_table.add_column("Status", style="green", justify="center")
    with Live(status_table, refresh_per_second=4) as live:
        live.update(status_table)
        for device_id in sorted(stopped_data):
            status_table.add_row(
                f"{device_id}", "[bold green]:heavy_check_mark:[/]"
            )
        for device_id in sorted(not_started):
            status_table.add_row(f"{device_id}", "[bold red]:x:[/]")


def print_stop_status(stopped_data: list[str], not_stopped: list[str]) -> None:
    """Print the stop status."""
    print("[bold]Stop status:[/]")
    status_table = Table()
    status_table.add_column("Device ID", style="magenta", no_wrap=True)
    status_table.add_column("Status", style="green", justify="center")
    with Live(status_table, refresh_per_second=4) as live:
        live.update(status_table)
        for device_id in sorted(stopped_data):
            status_table.add_row(
                f"{device_id}", "[bold green]:heavy_check_mark:[/]"
            )
        for device_id in sorted(not_stopped):
            status_table.add_row(f"{device_id}", "[bold red]:x:[/]")


def print_transfer_status(
    status: dict[str, TransferDataStatus], start_data: int
) -> None:
    """Print the transfer status."""
    print()
    print("[bold]Transfer status:[/]")
    transfer_status_table = Table()
    transfer_status_table.add_column(
        "Device ID", style="magenta", no_wrap=True
    )
    transfer_status_table.add_column(
        "Chunks acked", style="green", justify="center"
    )
    transfer_status_table.add_column(
        "Hashes match", style="green", justify="center"
    )
    with Live(transfer_status_table, refresh_per_second=4) as live:
        live.update(transfer_status_table)
        for device_id, status in sorted(status.items()):
            start_marker, stop_marker = (
                ("[bold green]", "[/]")
                if bool(status.hashes_match) is True
                else ("[bold red]", "[/]")
            )
            transfer_status_table.add_row(
                f"{device_id}",
                f"{len(status.chunks_acked)}/{start_data.chunks}",
                f"{start_marker}{bool(status.hashes_match)}{stop_marker}",
            )


def wait_for_done(timeout, condition_func):
    """Wait for the condition to be met."""
    while timeout > 0:
        if condition_func():
            return True
        timeout -= 0.01
        time.sleep(0.01)
    return False


@dataclass
class ControllerSettings:
    """Class that holds controller settings."""

    serial_port: str = SERIAL_PORT_DEFAULT
    serial_baudrate: int = 1000000
    mqtt_host: str = "argus.paris.inria.fr"
    mqtt_port: int = 8883
    edge: bool = False
    devices: list[str] = dataclasses.field(default_factory=lambda: [])


class Controller:
    """Class used to control a swarm testbed."""

    def __init__(self, settings: ControllerSettings):
        self.logger = LOGGER.bind(context=__name__)
        self.settings = settings
        self._interface: GatewayAdapterBase = None
        self.status_data: dict[str, StatusType] = {}
        self.started_data: list[str] = []
        self.stopped_data: list[str] = []
        self.chunks: list[DataChunk] = []
        self.start_ota_data: StartOtaData = StartOtaData()
        self.transfer_data: dict[str, TransferDataStatus] = {}
        self._known_devices: dict[str, StatusType] = {}
        self.expected_reply: Optional[SwarmitPayloadType] = None
        register_parsers()
        if self.settings.edge is True:
            self._interface = MQTTAdapter(
                self.settings.mqtt_host, self.settings.mqtt_port
            )
        else:
            try:
                self._interface = SerialAdapter(
                    self.settings.serial_port, self.settings.serial_baudrate
                )
            except (
                SerialInterfaceException,
                serial.serialutil.SerialException,
            ) as exc:
                console = Console()
                console.print(f"[bold red]Error:[/] {exc}")
        self._interface.init(self.on_data_received)

    @property
    def known_devices(self) -> dict[str, StatusType]:
        """Return the known devices."""
        if not self._known_devices:
            self._known_devices = self.status()
        return self._known_devices

    @property
    def running_devices(self) -> list[str]:
        """Return the running devices."""
        return [
            device_id
            for device_id, status in self.known_devices.items()
            if (
                status == StatusType.Running
                and (
                    not self.settings.devices
                    or device_id in self.settings.devices
                )
            )
        ]

    @property
    def resetting_devices(self) -> list[str]:
        """Return the resetting devices."""
        return [
            device_id
            for device_id, status in self.known_devices.items()
            if (
                status == StatusType.Resetting
                and (
                    not self.settings.devices
                    or device_id in self.settings.devices
                )
            )
        ]

    @property
    def ready_devices(self) -> list[str]:
        """Return the ready devices."""
        return [
            device_id
            for device_id, status in self.known_devices.items()
            if (
                status == StatusType.Bootloader
                and (
                    not self.settings.devices
                    or device_id in self.settings.devices
                )
            )
        ]

    @property
    def interface(self) -> GatewayAdapterBase:
        """Return the interface."""
        return self._interface

    def terminate(self):
        """Terminate the controller."""
        self.interface.close()

    def send_frame(self, frame: Frame):
        """Send a frame to the devices."""
        self.interface.send_data(frame.to_bytes())

    def on_data_received(self, data):
        frame = Frame().from_bytes(data)
        if frame.payload_type < SwarmitPayloadType.SWARMIT_REQUEST_STATUS:
            return
        device_id = f"{frame.payload.device_id:08X}"
        if (
            frame.payload_type
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_STATUS
            and self.expected_reply
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_STATUS
        ):
            self.status_data.update(
                {device_id: StatusType(frame.payload.status)}
            )
        elif (
            frame.payload_type
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_STARTED
            and self.expected_reply
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_STARTED
        ):
            if device_id not in self.started_data:
                self.started_data.append(device_id)
        elif (
            frame.payload_type
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_STOPPED
            and self.expected_reply
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_STOPPED
        ):
            if device_id not in self.stopped_data:
                self.stopped_data.append(device_id)
        elif (
            frame.payload_type
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_OTA_START_ACK
            and self.expected_reply
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_OTA_START_ACK
        ):
            if device_id not in self.start_ota_data.ids:
                self.start_ota_data.ids.append(device_id)
        elif (
            frame.payload_type
            == SwarmitPayloadType.SWARMIT_NOTIFICATION_OTA_CHUNK_ACK
        ):
            if (
                frame.payload.index
                not in self.transfer_data[device_id].chunks_acked
            ):
                self.transfer_data[device_id].chunks_acked.add(
                    frame.payload.index
                )
            self.transfer_data[device_id].hashes_match = (
                frame.payload.hashes_match
            )
        elif frame.payload_type in [
            SwarmitPayloadType.SWARMIT_NOTIFICATION_EVENT_GPIO,
            SwarmitPayloadType.SWARMIT_NOTIFICATION_EVENT_LOG,
        ]:
            if (
                self.settings.devices
                and device_id not in self.settings.devices
            ):
                return
            logger = self.logger.bind(
                deviceid=device_id,
                notification=frame.payload_type.name,
                timestamp=frame.payload.timestamp,
                data_size=frame.payload.count,
                data=frame.payload.data,
            )
            if (
                frame.payload_type
                == SwarmitPayloadType.SWARMIT_NOTIFICATION_EVENT_GPIO
            ):
                logger.info("GPIO event")
            elif (
                frame.payload_type
                == SwarmitPayloadType.SWARMIT_NOTIFICATION_EVENT_LOG
            ):
                logger.info("LOG event")
        elif frame.payload_type != self.expected_reply:
            self.logger.warning(
                "Unexpected payload",
                payload_type=hex(frame.payload_type),
                expected=hex(self.expected_reply),
            )
        else:
            self.logger.error(
                "Unknown payload type", payload_type=frame.payload_type
            )

    def status(self):
        """Request the status of the testbed."""
        self.status_data: dict[str, StatusType] = {}
        payload = PayloadStatusRequest(device_id=0)
        frame = Frame(header=Header(), payload=payload)
        self.expected_reply = SwarmitPayloadType.SWARMIT_NOTIFICATION_STATUS
        self.send_frame(frame)
        wait_for_done(1, lambda: False)
        return self.status_data

    def _send_start(self, device_id: str):
        def is_started():
            if device_id == "0":
                return sorted(self.started_data) == sorted(self.ready_devices)
            else:
                return device_id in self.started_data

        self.expected_reply = SwarmitPayloadType.SWARMIT_NOTIFICATION_STARTED
        payload = PayloadStartRequest(device_id=int(device_id, base=16))
        self.send_frame(Frame(header=Header(), payload=payload))
        wait_for_done(3, is_started)
        self.expected_reply = None

    def start(self):
        """Start the application."""
        self.started_data = []
        ready_devices = self.ready_devices
        if not self.settings.devices:
            self._send_start("0")
        else:
            for device_id in self.settings.devices:
                if device_id not in ready_devices:
                    continue
                self._send_start(device_id)
        return self.started_data

    def _send_stop(self, device_id: str):
        stoppable_devices = self.running_devices + self.resetting_devices

        def is_stopped():
            if device_id == "0":
                return sorted(self.stopped_data) == sorted(stoppable_devices)
            else:
                return device_id in self.stopped_data

        self.expected_reply = SwarmitPayloadType.SWARMIT_NOTIFICATION_STOPPED
        payload = PayloadStopRequest(device_id=int(device_id, base=16))
        self.send_frame(Frame(header=Header(), payload=payload))
        wait_for_done(3, is_stopped)
        self.expected_reply = None

    def stop(self):
        """Stop the application."""
        self.stopped_data = []
        stoppable_devices = self.running_devices + self.resetting_devices
        if not self.settings.devices:
            self._send_stop("0")
        else:
            for device_id in self.settings.devices:
                if device_id not in stoppable_devices:
                    continue
                self._send_stop(device_id)
        return self.stopped_data

    def _send_reset(self, device_id: str, location: ResetLocation):
        payload = PayloadResetRequest(
            device_id=int(device_id, base=16),
            pos_x=location.pos_x,
            pos_y=location.pos_y,
        )
        self.send_frame(Frame(header=Header(), payload=payload))

    def reset(self, locations: dict[str, ResetLocation]):
        """Reset the application."""
        ready_devices = self.ready_devices
        for device_id in self.settings.devices:
            if device_id not in ready_devices:
                continue
            print(
                f"Resetting device {device_id} with location {locations[device_id]}"
            )
            self._send_reset(device_id, locations[device_id])

    def monitor(self):
        """Monitor the testbed."""
        self.logger.info("Monitoring testbed")
        while True:
            time.sleep(0.01)

    def _send_message(self, device_id, message):
        payload = PayloadMessage(
            device_id=int(device_id, base=16),
            count=len(message),
            message=message.encode(),
        )
        frame = Frame(header=Header(), payload=payload)
        self.send_frame(frame)

    def send_message(self, message):
        """Send a message to the devices."""
        running_devices = self.running_devices
        if not self.settings.devices:
            self._send_message("0", message)
        else:
            for device_id in self.settings.devices:
                if device_id not in running_devices:
                    continue
                self._send_message(device_id, message)

    def _send_start_ota(self, device_id: str, firmware: bytes):

        def is_start_ota_acknowledged():
            if device_id == "0":
                return sorted(self.start_ota_data.ids) == sorted(
                    self.ready_devices
                )
            else:
                return device_id in self.start_ota_data.ids

        payload = PayloadOTAStartRequest(
            device_id=int(device_id, base=16),
            fw_length=len(firmware),
            fw_chunk_count=len(self.chunks),
            fw_hash=self.fw_hash,
        )
        self.send_frame(Frame(header=Header(), payload=payload))
        wait_for_done(3, is_start_ota_acknowledged)

    def start_ota(self, firmware) -> StartOtaData:
        """Start the OTA process."""
        self.start_ota_data = StartOtaData()
        self.chunks = []
        digest = hashes.Hash(hashes.SHA256())
        chunks_count = int(len(firmware) / CHUNK_SIZE) + int(
            len(firmware) % CHUNK_SIZE != 0
        )
        for chunk_idx in range(chunks_count):
            if chunk_idx == chunks_count - 1:
                chunk_size = len(firmware) % CHUNK_SIZE
            else:
                chunk_size = CHUNK_SIZE
            data = firmware[
                chunk_idx * CHUNK_SIZE : chunk_idx * CHUNK_SIZE + chunk_size
            ]
            digest.update(data)
            self.chunks.append(
                DataChunk(
                    index=chunk_idx,
                    size=chunk_size,
                    data=data,
                )
            )
        self.fw_hash = digest.finalize()
        self.expected_reply = (
            SwarmitPayloadType.SWARMIT_NOTIFICATION_OTA_START_ACK
        )
        self.start_ota_data.fw_hash = self.fw_hash
        self.start_ota_data.chunks = len(self.chunks)
        if not self.settings.devices:
            print("Broadcast start ota notification...")
            self._send_start_ota("0", firmware)
        else:
            for device_id in self.settings.devices:
                print(f"Sending start ota notification to {device_id}...")
                self._send_start_ota(device_id, firmware)
        self.expected_reply = None
        return self.start_ota_data

    def send_chunk(self, chunk, device_id: str):

        def is_chunk_acknowledged():
            if device_id == "0":
                return sorted(self.transfer_data.keys()) == sorted(
                    self.ready_devices
                ) and all(
                    [
                        chunk.index in status.chunks_acked
                        for status in self.transfer_data.values()
                    ]
                )
            else:
                return (
                    device_id in self.transfer_data.keys()
                    and chunk.index
                    in self.transfer_data[device_id].chunks_acked
                )

        send_time = time.time()
        send = True
        tries = 0
        while tries < 3:
            if is_chunk_acknowledged():
                break
            if send is True:
                payload = PayloadOTAChunkRequest(
                    device_id=int(device_id, base=16),
                    index=chunk.index,
                    count=chunk.size,
                    chunk=chunk.data,
                )
                self.send_frame(Frame(header=Header(), payload=payload))
                if device_id == "0":
                    for device_id in self.ready_devices:
                        self.transfer_data[device_id].retries[
                            chunk.index
                        ] = tries
                else:
                    self.transfer_data[device_id].retries[chunk.index] = tries
                tries += 1
                time.sleep(0.01)
                send_time = time.time()
            time.sleep(0.001)
            send = time.time() - send_time > 1

    def transfer(self, firmware):
        """Transfer the firmware to the devices."""
        data_size = len(firmware)
        progress = tqdm(
            range(0, data_size),
            unit="B",
            unit_scale=False,
            colour="green",
            ncols=100,
        )
        progress.set_description(
            f"Loading firmware ({int(data_size / 1024)}kB)"
        )
        self.expected_reply = (
            SwarmitPayloadType.SWARMIT_NOTIFICATION_OTA_CHUNK_ACK
        )
        self.transfer_data = {}
        if not self.settings.devices:
            for device_id in self.ready_devices:
                self.transfer_data[device_id] = TransferDataStatus()
                self.transfer_data[device_id].retries = [0] * len(self.chunks)
        else:
            for device_id in self.settings.devices:
                self.transfer_data[device_id] = TransferDataStatus()
                self.transfer_data[device_id].retries = [0] * len(self.chunks)
        for chunk in self.chunks:
            if not self.settings.devices:
                self.send_chunk(chunk, "0")
            else:
                for device_id in self.settings.devices:
                    self.send_chunk(chunk, device_id)
            progress.update(chunk.size)
        progress.close()
        self.expected_reply = None
        return self.transfer_data
