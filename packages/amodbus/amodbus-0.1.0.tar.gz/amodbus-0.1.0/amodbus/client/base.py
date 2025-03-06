"""Base for all clients."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from amodbus.client.mixin import ModbusClientMixin
from amodbus.exceptions import ConnectionException
from amodbus.framer import FRAMER_NAME_TO_CLASS, FramerBase, FramerType
from amodbus.logging import Log
from amodbus.pdu import DecodePDU, ModbusPDU
from amodbus.transaction import TransactionManager
from amodbus.transport import CommParams


class ModbusBaseClient(ModbusClientMixin[Awaitable[ModbusPDU]]):
    """**ModbusBaseClient**.

    :mod:`ModbusBaseClient` is normally not referenced outside :mod:`amodbus`.
    """

    def __init__(
        self,
        framer: FramerType,
        retries: int,
        comm_params: CommParams,
        trace_packet: Callable[[bool, bytes], bytes] | None,
        trace_pdu: Callable[[bool, ModbusPDU], ModbusPDU] | None,
        trace_connect: Callable[[bool], None] | None,
    ) -> None:
        """Initialize a client instance.

        :meta private:
        """
        ModbusClientMixin.__init__(self)  # type: ignore[arg-type]
        self.comm_params = comm_params
        self.ctx = TransactionManager(
            comm_params,
            (FRAMER_NAME_TO_CLASS[framer])(DecodePDU(False)),
            retries,
            False,
            trace_packet,
            trace_pdu,
            trace_connect,
        )

    @property
    def connected(self) -> bool:
        """Return state of connection."""
        return self.ctx.is_active()

    async def connect(self) -> bool:
        """Call transport connect."""
        self.ctx.reset_delay()
        Log.debug(
            "Connecting to {}:{}.",
            self.ctx.comm_params.host,
            self.ctx.comm_params.port,
        )
        rc = await self.ctx.connect()
        await asyncio.sleep(0.1)
        return rc

    def register(self, custom_response_class: type[ModbusPDU]) -> None:
        """Register a custom response class with the decoder (call **sync**).

        :param custom_response_class: (optional) Modbus response class.
        :raises MessageRegisterException: Check exception text.

        Use register() to add non-standard responses (like e.g. a login prompt) and
        have them interpreted automatically.
        """
        self.ctx.framer.decoder.register(custom_response_class)

    def close(self) -> None:
        """Close connection."""
        self.ctx.close()

    def execute(self, no_response_expected: bool, request: ModbusPDU):
        """Execute request and get response (call **sync/async**).

        :meta private:
        """
        if not self.ctx.transport:
            raise ConnectionException(f"Not connected[{self!s}]")
        return self.ctx.execute(no_response_expected, request)

    def set_max_no_responses(self, max_count: int) -> None:
        """Override default max no request responses.

        :param max_count: Max aborted requests before disconnecting.

        The parameter retries defines how many times a request is retried
        before being aborted. Once aborted a counter is incremented, and when
        this counter is greater than max_count the connection is terminated.

        .. tip::
            When a request is successful the count is reset.
        """
        self.ctx.max_until_disconnect = max_count

    async def __aenter__(self):
        """Implement the client with enter block.

        :returns: The current instance of the client
        :raises ConnectionException:
        """
        await self.connect()
        return self

    async def __aexit__(self, klass, value, traceback):
        """Implement the client with aexit block."""
        self.close()

    def __str__(self):
        """Build a string representation of the connection.

        :returns: The string representation
        """
        return f"{self.__class__.__name__} {self.ctx.comm_params.host}:{self.ctx.comm_params.port}"
