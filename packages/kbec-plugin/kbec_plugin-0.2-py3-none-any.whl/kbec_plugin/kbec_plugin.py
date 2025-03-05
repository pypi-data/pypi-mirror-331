from .kbec_config import KBecConfig
from logging import Logger

from typing import Any
from berconpy.asyncio.player import Player
from berconpy.asyncio.dispatch import AsyncEventDispatcher

class KBecPlugin:
    def __init__(self, config_path: str, _kbec_client: object):
        self.config = KBecConfig(config_path)
        self.logger: Logger = None
        self._kbec_client = _kbec_client

    def _set_logger(self, logger: Logger):
        self.logger = logger

    def _add_event_listeners(self):
        dispatch: AsyncEventDispatcher = self._kbec_client.rcon_manager.dispatch

        for event in self.events:
            dispatch.add_listener(event, getattr(self, event))

    @property
    def plugin_info(self) -> str:
        return self.config.plugin_info

    @property
    def events(self) -> set[str]:
        return {"on_login", "on_command", "on_message", "on_admin_login",
                "on_player_connect", "on_player_guid", "on_player_verify_guid",
                "on_player_disconnect", "on_player_kick", "on_admin_message",
                "on_admin_announcement", "on_admin_whisper", "on_player_message"}

    # Refer to https://github.com/thegamecracks/berconpy/blob/main/src/berconpy/dispatch.py for docs on these events

    async def on_login(self, /) -> Any:
        pass

    async def on_command(self, response: str, /) -> Any:
        pass

    async def on_message(self, message: str, /) -> Any:
        pass

    async def on_admin_login(self, admin_id: int, addr: str, /) -> Any:
        pass

    async def on_player_connect(self, player: Player, /) -> Any:
        pass

    async def on_player_guid(self, player: Player, /) -> Any:
        pass

    async def on_player_verify_guid(self, player: Player, /) -> Any:
        pass

    async def on_player_disconnect(self, player: Player, /) -> Any:
        pass

    async def on_player_kick(self, player: Player, reason: str, /) -> Any:
        pass

    async def on_admin_message(self, admin_id: int, channel: str, message: str, /) -> Any:
        pass

    async def on_admin_announcement(self, admin_id: int, message: str, /) -> Any:
        pass

    async def on_admin_whisper(self, player: Player, admin_id: int, message: str, /) -> Any:
        pass

    async def on_player_message(self, player: Player, channel: str, message: str, /) -> Any:
        pass