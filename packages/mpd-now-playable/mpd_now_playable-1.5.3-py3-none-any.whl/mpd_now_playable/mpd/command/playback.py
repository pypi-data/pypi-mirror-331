from dataclasses import dataclass, field
from typing import Annotated, Literal

from annotated_types import Ge
from mpd.asyncio import MPDClient

from ...playback.state import PlaybackState
from .types import Command


@dataclass
class Toggle(Command[PlaybackState]):
	cmd: Literal["toggle"] = field(default="toggle", repr=False)

	async def apply(self, mpd: MPDClient) -> PlaybackState:
		status = await mpd.status()
		command = choose_toggle_action(status["state"])(self.id)
		return await command.apply(mpd)


@dataclass
class Play(Command[PlaybackState]):
	cmd: Literal["play"] = field(default="play", repr=False)

	async def apply(self, mpd: MPDClient) -> PlaybackState:
		await mpd.play()
		return PlaybackState.play


@dataclass
class Pause(Command[PlaybackState]):
	cmd: Literal["pause"] = field(default="pause", repr=False)

	async def apply(self, mpd: MPDClient) -> PlaybackState:
		await mpd.pause(1)
		return PlaybackState.pause


@dataclass
class Stop(Command[PlaybackState]):
	cmd: Literal["stop"] = field(default="stop", repr=False)

	async def apply(self, mpd: MPDClient) -> PlaybackState:
		await mpd.stop()
		return PlaybackState.stop


@dataclass
class Next(Command[None]):
	cmd: Literal["next"] = field(default="next", repr=False)

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.next()


@dataclass
class Previous(Command[None]):
	cmd: Literal["previous"] = field(default="previous", repr=False)

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.previous()


@dataclass(kw_only=True)
class SeekBy(Command[None]):
	cmd: Literal["seek_by"] = field(default="seek_by", repr=False)
	seconds: float

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.seekcur(f"{self.seconds:+}")


@dataclass(kw_only=True)
class SeekTo(Command[None]):
	cmd: Literal["seek_to"] = field(default="seek_to", repr=False)
	seconds: Annotated[float, Ge(0)]

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.seekcur(self.seconds)


def choose_toggle_action(state: Literal["play", "pause", "stop"]) -> type[Play | Pause]:
	match state:
		case "play":
			return Pause
		case "pause" | "stop":
			return Play


type PlaybackCommand = Toggle | Play | Pause | Stop | Next | Previous | SeekBy | SeekTo
