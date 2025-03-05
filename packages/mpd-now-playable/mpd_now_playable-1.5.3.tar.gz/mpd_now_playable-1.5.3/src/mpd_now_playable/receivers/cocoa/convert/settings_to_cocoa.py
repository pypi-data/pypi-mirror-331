from dataclasses import dataclass

from MediaPlayer import (
	MPRepeatType,
	MPRepeatTypeAll,
	MPRepeatTypeOff,
	MPRepeatTypeOne,
	MPShuffleType,
	MPShuffleTypeItems,
	MPShuffleTypeOff,
)

from ....playback.settings import Settings


@dataclass
class CocoaSettings:
	repeat: MPRepeatType
	shuffle: MPShuffleType


def to_repeat(settings: Settings) -> MPRepeatType:
	if not settings.repeat:
		return MPRepeatTypeOff
	if settings.single:
		return MPRepeatTypeOne
	return MPRepeatTypeAll


def to_shuffle(settings: Settings) -> MPShuffleType:
	if settings.random:
		return MPShuffleTypeItems
	return MPShuffleTypeOff


def settings_to_cocoa(settings: Settings) -> CocoaSettings:
	return CocoaSettings(to_repeat(settings), to_shuffle(settings))
