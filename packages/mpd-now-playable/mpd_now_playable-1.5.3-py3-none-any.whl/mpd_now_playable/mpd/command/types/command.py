from abc import abstractmethod
from dataclasses import dataclass

from mpd.asyncio import MPDClient


@dataclass
class Command[T]:
	id: int

	@abstractmethod
	async def apply(self, mpd: MPDClient) -> T: ...


@dataclass
class Response[T]:
	id: int
	command: Command[T]
	result: T
