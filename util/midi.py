from util.enum import Enum


class Status(Enum):
    NoteOn = 0x90
    NoteOff = 0x80


def get_status_without_channel(message):
    return message.status & ~0x0F


def is_note_on_message(message):
    return get_status_without_channel(message) == Status.NoteOn


def is_note_off_message(message):
    return get_status_without_channel(message) == Status.NoteOff


def is_note_message(message):
    return is_note_on_message(message) or is_note_off_message(message)


def get_sysex(message):
    if message.sysex:
        return list(message.sysex)[1:-1]
    return None
