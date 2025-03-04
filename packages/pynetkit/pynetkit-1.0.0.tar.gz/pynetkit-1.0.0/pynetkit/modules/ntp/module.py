#  Copyright (c) Kuba Szczodrzyński 2024-10-25.

from datetime import datetime
from ipaddress import IPv4Address
from socket import (
    AF_INET,
    IPPROTO_UDP,
    SO_BROADCAST,
    SO_REUSEADDR,
    SOCK_DGRAM,
    SOL_SOCKET,
    socket,
)

from pynetkit.modules.base import ModuleBase

from .events import NtpSyncEvent
from .structs import NtpPacket


class NtpModule(ModuleBase):
    PRE_RUN_CONFIG = ["address", "port"]
    # pre-run configuration
    address: IPv4Address
    port: int
    # runtime configuration
    # server handle
    _sock: socket | None = None

    def __init__(self):
        super().__init__()
        self.address = IPv4Address("0.0.0.0")
        self.port = 123

    async def run(self) -> None:
        self.info(f"Starting NTP server on {self.address}:{self.port}")
        self._sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._sock.bind((str(self.address), self.port))
        while self.should_run and self._sock is not None:
            self._process_request()

    async def stop(self) -> None:
        await self.cleanup()
        await super().stop()

    async def cleanup(self) -> None:
        if self._sock:
            self._sock.close()
        self._sock = None

    def _process_request(self) -> None:
        request, addr = self._sock.recvfrom(4096)
        address = IPv4Address(addr[0])
        try:
            packet = NtpPacket.unpack(request)
        except Exception as e:
            self.warning(f"Invalid NTP packet: {e}")
            return

        now = datetime.now()
        packet = NtpPacket(
            flags=NtpPacket.Flags(li=0, vn=3, mode=4),
            stratum=1,
            ppoll=2.0,
            precision=0.0625,
            refid=b"NIST",
            reftime=now,
            org=packet.xmt,
            rec=now,
            xmt=now,
        )
        response = packet.pack()

        # copy the ntp.xmt timestamp to ntp.org at byte-level
        # some clients compare these two, but conversion to datetime() loses precision
        response = response[0:24] + request[40:48] + response[32:48]

        self.debug(f"NTP request from {address}")
        self._sock.sendto(response, addr)
        NtpSyncEvent(
            address=address,
            origin_timestamp=packet.org,
        ).broadcast()
