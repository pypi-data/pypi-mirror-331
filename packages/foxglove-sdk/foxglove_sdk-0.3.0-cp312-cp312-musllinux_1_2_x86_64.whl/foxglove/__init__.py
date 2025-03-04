"""
This module provides interfaces for logging messages to Foxglove.

See :py:mod:`foxglove.schemas` and :py:mod:`foxglove.channels` for working with well-known Foxglove
schemas.
"""

import atexit
import logging
from typing import Callable, List, Optional, Protocol, Union

from ._foxglove_py import (
    Capability,
    ChannelView,
    Client,
    ConnectionGraph,
    MCAPWriter,
    MessageSchema,
    Parameter,
    ParameterType,
    ParameterValue,
    Schema,
    Service,
    ServiceRequest,
    ServiceSchema,
    StatusLevel,
    WebSocketServer,
    enable_logging,
    open_mcap,
    shutdown,
)
from ._foxglove_py import start_server as _start_server
from .channel import Channel, log

atexit.register(shutdown)


class ServerListener(Protocol):
    """
    A mechanism to register callbacks for handling client message events.
    """

    def on_subscribe(self, client: Client, channel: ChannelView) -> None:
        """
        Called by the server when a client subscribes to a channel.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param channel: The channel (id, topic) that the message was sent on.
        :type channel: :py:class:`ChannelView`
        """
        return None

    def on_unsubscribe(self, client: Client, channel: ChannelView) -> None:
        """
        Called by the server when a client unsubscribes from a channel.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param channel: The channel (id, topic) that the message was sent on.
        :type channel: :py:class:`ChannelView`
        """
        return None

    def on_client_advertise(self, client: Client, channel: ChannelView) -> None:
        """
        Called by the server when a client advertises a channel.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param channel: The channel (id, topic) that the message was sent on.
        :type channel: :py:class:`ChannelView`
        """
        return None

    def on_client_unadvertise(self, client: Client, channel: ChannelView) -> None:
        """
        Called by the server when a client unadvertises a channel.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param channel: The channel (id, topic) that the message was sent on.
        :type channel: :py:class:`ChannelView`
        """
        return None

    def on_message_data(
        self, client: Client, channel: ChannelView, data: bytes
    ) -> None:
        """
        Called by the server when a message is received from a client.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param channel: The channel (id, topic) that the message was sent on.
        :type channel: :py:class:`ChannelView`
        :param data: The message data.
        :type data: bytes
        """
        return None

    def on_get_parameters(
        self,
        client: Client,
        param_names: List[str],
        request_id: Optional[str] = None,
    ) -> List["Parameter"]:
        """
        Called by the server when a client requests parameters.

        Requires :py:data:`Capability.Parameters`.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param param_names: The names of the parameters to get.
        :type param_names: list[str]
        :param request_id: An optional request id.
        :type request_id: Optional[str]
        """
        return []

    def on_set_parameters(
        self,
        client: Client,
        parameters: List["Parameter"],
        request_id: Optional[str] = None,
    ) -> List["Parameter"]:
        """
        Called by the server when a client sets parameters.
        Note that only `parameters` which have changed are included in the callback, but the return
        value must include all parameters.

        Requires :py:data:`Capability.Parameters`.

        :param client: The client (id) that sent the message.
        :type client: :py:class:`Client`
        :param parameters: The parameters to set.
        :type parameters: list[:py:class:`Parameter`]
        :param request_id: An optional request id.
        :type request_id: Optional[str]
        """
        return parameters

    def on_parameters_subscribe(
        self,
        param_names: List[str],
    ) -> None:
        """
        Called by the server when a client subscribes to one or more parameters for the first time.

        Requires :py:data:`Capability.Parameters`.

        :param param_names: The names of the parameters to subscribe to.
        :type param_names: list[str]
        """
        return None

    def on_parameters_unsubscribe(
        self,
        param_names: List[str],
    ) -> None:
        """
        Called by the server when the last client subscription to one or more parameters has been
        removed.

        Requires :py:data:`Capability.Parameters`.

        :param param_names: The names of the parameters to unsubscribe from.
        :type param_names: list[str]
        """
        return None

    def on_connection_graph_subscribe(self) -> None:
        """
        Called by the server when the first client subscribes to the connection graph.
        """
        return None

    def on_connection_graph_unsubscribe(self) -> None:
        """
        Called by the server when the last client unsubscribes from the connection graph.
        """
        return None


# Redefine types from the stub interface so they're available for documentation.
ServiceHandler = Callable[["ServiceRequest"], bytes]
AssetHandler = Callable[[str], Optional[bytes]]


def start_server(
    *,
    name: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 8765,
    capabilities: Optional[List[Capability]] = None,
    server_listener: Optional[ServerListener] = None,
    supported_encodings: Optional[List[str]] = None,
    services: Optional[List[Service]] = None,
    asset_handler: Optional[AssetHandler] = None,
) -> WebSocketServer:
    """
    Start a websocket server for live visualization.

    :param name: The name of the server.
    :type name: Optional[str]
    :param host: The host to bind to.
    :type host: Optional[str] = "127.0.0.1"
    :param port: The port to bind to.
    :type port: Optional[int] = 8765
    :param capabilities: A list of capabilities to advertise to clients.
    :type capabilities: Optional[List[Capability]] = None
    :param server_listener: A Python object that implements the :py:class:`ServerListener` protocol.
    :type server_listener: Optional[ServerListener] = None
    :param supported_encodings: A list of encodings to advertise to clients.
    :type supported_encodings: Optional[List[str]] = None
    :param services: A list of services to advertise to clients.
    :type services: Optional[List[Service]] = None
    :param asset_handler: A callback function that returns the asset for a given URI, or None if
        it doesn't exist.
    :type asset_handler: Optional[:py:class:`AssetHandler`] = None
    """
    return _start_server(
        name=name,
        host=host,
        port=port,
        capabilities=capabilities,
        server_listener=server_listener,
        supported_encodings=supported_encodings,
        services=services,
        asset_handler=asset_handler,
    )


def set_log_level(level: Union[int, str] = "INFO") -> None:
    """
    Enable SDK logging.

    This function will call logging.basicConfig() for convenience in scripts, but in general you
    should configure logging yourself before calling this function:
    https://docs.python.org/3/library/logging.html

    :param level: The logging level to set. This accepts the same values as `logging.setLevel` and
        defaults to "INFO". The SDK will not log at levels "CRITICAL" or higher.
    """
    # This will raise a ValueError for invalid levels if the user has not already configured
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")

    if isinstance(level, str):
        level_map = (
            logging.getLevelNamesMapping()
            if hasattr(logging, "getLevelNamesMapping")
            else _level_names()
        )
        try:
            level = level_map[level]
        except KeyError:
            raise ValueError(f"Unknown log level: {level}")
    else:
        level = max(0, min(2**32 - 1, level))

    enable_logging(level)


def _level_names() -> dict[str, int]:
    # Fallback for Python <3.11; no support for custom levels
    return {
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "ERROR": logging.ERROR,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }


__all__ = [
    "Capability",
    "Channel",
    "ChannelView",
    "Client",
    "ConnectionGraph",
    "MCAPWriter",
    "MessageSchema",
    "Parameter",
    "ParameterType",
    "ParameterValue",
    "Schema",
    "ServerListener",
    "Service",
    "ServiceHandler",
    "ServiceRequest",
    "ServiceSchema",
    "StatusLevel",
    "WebSocketServer",
    "log",
    "open_mcap",
    "set_log_level",
    "start_server",
]
