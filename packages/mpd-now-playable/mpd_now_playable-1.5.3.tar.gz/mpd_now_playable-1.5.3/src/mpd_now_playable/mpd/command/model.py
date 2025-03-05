from dataclasses import dataclass
from typing import Annotated

from pydantic import Field

from ...tools.schema.define import schema
from .playback import PlaybackCommand
from .queue import QueueCommand
from .settings import SettingsCommand


@schema("https://cdn.00dani.me/m/schemata/mpd-now-playable/command-v1.json")
@dataclass
class MpdCommand:
	commands: list[
		Annotated[
			PlaybackCommand | QueueCommand | SettingsCommand, Field(discriminator="cmd")
		]
	]
