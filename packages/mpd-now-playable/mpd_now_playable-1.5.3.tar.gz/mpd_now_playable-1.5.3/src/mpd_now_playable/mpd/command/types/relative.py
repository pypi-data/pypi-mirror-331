from dataclasses import dataclass
from typing import Annotated

from annotated_types import Ge

# The basic numeric types Python supports other than complex. The term "real"
# can also imply "every real number, not just the integers", but that's not the
# intent here.
type Real = int | float


@dataclass
class Absolute[T: Real]:
	abs: Annotated[T, Ge(0)]

	def to_arg(self) -> str:
		return f"{self.abs:-}"


@dataclass
class Relative[T: Real]:
	rel: T

	def to_arg(self) -> str:
		return f"{self.rel:+}"


type Position[T: Real] = Absolute[T] | Relative[T]
type SeekPosition = Position[float]
type Index = Position[int]
