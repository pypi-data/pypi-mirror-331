from dataclasses import dataclass, field
from typing import Literal, Optional

from mpd.asyncio import MPDClient

from ...tools.schema.fields import Url
from ...tools.types import option_fmap
from .types import Command


@dataclass(kw_only=True)
class Add(Command[Optional[int]]):
	cmd: Literal["add"] = field(default="add", repr=False)
	uri: Url

	async def apply(self, mpd: MPDClient) -> Optional[int]:
		song_id = await mpd.addid(self.uri.human_repr())
		return option_fmap(int, song_id)


@dataclass(kw_only=True)
class Delete(Command[None]):
	cmd: Literal["delete"] = field(default="delete", repr=False)
	songid: int

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.deleteid(self.songid)


@dataclass
class Clear(Command[None]):
	cmd: Literal["clear"] = field(default="clear", repr=False)

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.clear()


@dataclass
class Shuffle(Command[None]):
	cmd: Literal["shuffle"] = field(default="shuffle", repr=False)

	async def apply(self, mpd: MPDClient) -> None:
		await mpd.shuffle()


type QueueCommand = Add | Delete | Clear | Shuffle
