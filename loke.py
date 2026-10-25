# coding=UTF-8
"""Slack transport and module dispatch for Loke."""

import logging
import os
from threading import Event

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse


LOGGER = logging.getLogger(__name__)


class LokeEventHandler:
    """Interface implemented by Loke modules."""

    def handle_message(self, event):
        raise NotImplementedError()

    def handle_presence_change(self, event):
        raise NotImplementedError()

    def handle_loop(self):
        raise NotImplementedError()


class Loke:
    """Connect Loke's existing modules to a Slack app via Socket Mode."""

    def __init__(self, config):
        self.config = config
        self.sc = None
        self.socket_mode_client = None
        self.bot_token = None
        self._handlers = []

    def register_handler(self, handler):
        self._handlers.append(handler)

    def handle_message(self, event=None, **payload):
        """Dispatch one Slack Events API message to registered modules.

        ``payload['data']`` is accepted for compatibility with the old RTM
        callback shape, which also makes this method straightforward to test.
        """
        event = event or payload.get("data") or {}

        # Edits, deletions and bot messages use the same event family. They are
        # not commands and can cause reply loops, so only normal user messages
        # and file shares are dispatched.
        if event.get("bot_id") or event.get("user") == self.config.get("ownid"):
            return
        if event.get("subtype") not in (None, "file_share"):
            return
        if not event.get("channel"):
            return

        # Existing modules expect a text key, including for file-share events.
        event.setdefault("text", "")

        if event["text"] == ".modules":
            modules = "\n".join(
                " - %s" % handler.handler_version() for handler in self._handlers
            )
            self.sc.chat_postMessage(
                channel=event["channel"], text="*Loaded modules*\n%s" % modules
            )

        for handler in self._handlers:
            try:
                handler.handle_message(event)
            except Exception:
                # One broken external-data module should not prevent the other
                # bot commands from being handled.
                LOGGER.exception(
                    "Module %s failed while handling a Slack message",
                    handler.__class__.__name__,
                )

    def handle_presence_change(self, event=None, **payload):
        """Compatibility hook for modules that used legacy RTM presence.

        Slack's modern Events API / Socket Mode does not expose presence
        subscriptions. This method remains callable by local code, but it is
        deliberately not registered with Socket Mode.
        """
        event = event or payload.get("data") or {}
        for handler in self._handlers:
            handler.handle_presence_change(event)

    def _process_socket_mode_request(
        self, client: SocketModeClient, request: SocketModeRequest
    ):
        """Acknowledge a Socket Mode envelope and dispatch message events."""
        if request.envelope_id:
            client.send_socket_mode_response(
                SocketModeResponse(envelope_id=request.envelope_id)
            )

        if request.type != "events_api":
            return

        event = request.payload.get("event", {})
        if event.get("type") == "message":
            self.handle_message(event)

    def init(self):
        """Initialize Slack Web API and Socket Mode clients."""
        # Environment variables keep secrets out of config.py and take
        # precedence. ``token`` remains a migration fallback for old installs.
        self.bot_token = (
            os.getenv("SLACK_BOT_TOKEN")
            or self.config.get("bot_token")
            or self.config.get("token")
        )
        app_token = os.getenv("SLACK_APP_TOKEN") or self.config.get("app_token")

        missing = []
        if not self.bot_token:
            missing.append("SLACK_BOT_TOKEN (xoxb-...)")
        if not app_token:
            missing.append("SLACK_APP_TOKEN (xapp-...)")
        if missing:
            raise ValueError("Missing Slack credentials: %s" % ", ".join(missing))

        self.sc = WebClient(token=self.bot_token)
        self.socket_mode_client = SocketModeClient(
            app_token=app_token,
            web_client=self.sc,
        )
        self.socket_mode_client.socket_mode_request_listeners.append(
            self._process_socket_mode_request
        )
        return self

    def loop(self):
        """Connect to Slack and keep the Socket Mode connection alive."""
        if self.socket_mode_client is None:
            raise RuntimeError("Call init() before loop()")

        self.socket_mode_client.connect()
        LOGGER.info("Loke is connected to Slack using Socket Mode")
        Event().wait()

