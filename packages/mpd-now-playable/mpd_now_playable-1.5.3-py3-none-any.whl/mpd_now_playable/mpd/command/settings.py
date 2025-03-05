from dataclasses import dataclass, field
from typing import Annotated, Literal, TypeAlias

from annotated_types import Ge
from mpd.asyncio import MPDClient

from .types import Command

type OneShotFlag = bool | Literal["oneshot"]
type ReplayGainMode = Literal["off", "track", "album", "auto"]

# Defining this particular alias with a `type` statement makes Mypy complain
# because Ge(0) is a value and is not a valid type, but it's supposed to work
# because typing.Annotated requires only its first parameter to be a type
# expression. It does work totally fine if you use the older typing.TypeAlias
# syntax instead. Weird.
NonNegativeInt: TypeAlias = Annotated[int, Ge(0)]


@dataclass(kw_only=True)
class Consume(Command[OneShotFlag]):
	cmd: Literal["consume"] = field(default="consume", repr=False)
	mode: OneShotFlag

	async def apply(self, mpd: MPDClient) -> OneShotFlag:
		if self.mode == "oneshot":
			await mpd.consume("oneshot")
		else:
			await mpd.consume(1 if self.mode else 0)
		return self.mode


@dataclass(kw_only=True)
class Single(Command[OneShotFlag]):
	cmd: Literal["single"] = field(default="single", repr=False)
	mode: OneShotFlag

	async def apply(self, mpd: MPDClient) -> OneShotFlag:
		if self.mode == "oneshot":
			await mpd.single("oneshot")
		else:
			await mpd.single(1 if self.mode else 0)
		return self.mode


@dataclass(kw_only=True)
class Repeat(Command[bool]):
	cmd: Literal["repeat"] = field(default="repeat", repr=False)
	mode: bool

	async def apply(self, mpd: MPDClient) -> bool:
		await mpd.repeat(1 if self.mode else 0)
		return self.mode


@dataclass(kw_only=True)
class Random(Command[bool]):
	cmd: Literal["random"] = field(default="random", repr=False)
	mode: bool

	async def apply(self, mpd: MPDClient) -> bool:
		await mpd.random(1 if self.mode else 0)
		return self.mode


@dataclass(kw_only=True)
class Crossfade(Command[NonNegativeInt]):
	cmd: Literal["crossfade"] = field(default="crossfade", repr=False)
	seconds: NonNegativeInt

	async def apply(self, mpd: MPDClient) -> NonNegativeInt:
		await mpd.crossfade(self.seconds)
		return self.seconds


@dataclass(kw_only=True)
class SetReplayGainMode(Command[ReplayGainMode]):
	cmd: Literal["replay_gain_mode"] = field(default="replay_gain_mode", repr=False)
	mode: ReplayGainMode

	async def apply(self, mpd: MPDClient) -> ReplayGainMode:
		await mpd.replay_gain_mode(self.mode)
		return self.mode


type SettingsCommand = (
	Consume | Single | Repeat | Random | Crossfade | SetReplayGainMode
)
