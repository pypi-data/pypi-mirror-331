"""Extracts events from a midifile."""

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Union, cast

from mido import Message, MidiTrack
from mido.midifiles.meta import MetaMessage
from mido.midifiles.midifiles import MidiFile

from midiutils.types import NoteEvent


class MidiPreprocessor:
  def __init__(self) -> None:
    self.events: List[NoteEvent] = []

  def _initialize_note(
    self,
    temp: Dict[int, NoteEvent | None],
    note: int,
    velocity: int,
    time: int,
    hand: Literal["left", "right"],
  ) -> None:
    temp_note = NoteEvent(note, velocity, time, hand=hand)
    temp[note] = temp_note

  def _handle_note_off(
    self, temp: Dict[int, NoteEvent | None], msg_note: int, time: int
  ) -> None:
    for note in temp.values():
      if not note:
        continue
      elif note.end == 0 and note.note == msg_note:
        note.set_end(time)
        self.events.append(note)
        temp[msg_note] = None

  def _preprocess_track(
    self,
    track: Iterable[Union[Message, MetaMessage]],
    hand: Literal["right", "left"],
  ) -> None:
    time: int = 0  # The cumulative time across the whole song
    active_notes: Dict[int, NoteEvent | None] = {}
    for _, msg in enumerate(track):
      time_t = msg.time
      time += time_t
      # Skip meta messages and unsupported types
      if isinstance(msg, MetaMessage) or not hasattr(msg, "note"):
        continue
      note, velocity, note = msg.note, msg.velocity, msg.note
      msg_type = cast(str, msg.type)
      if msg_type == "note_on" and velocity != 0:  # Starting note
        self._initialize_note(active_notes, note, velocity, time, hand)
      elif (
        msg_type == "note_on" and velocity == 0
      ):  # Note on with velocity 0 is note off
        self._handle_note_off(active_notes, note, time)
      elif msg_type == "note_off":  # Note off
        self._handle_note_off(active_notes, note, time)

  def _extract_midi_objects(self, midi_path: Path) -> None:
    """Extracts the notes and pedal events from a midi file
    The note from channel 0 is assigned to the left hand and the notes from
    channel 1 are assigned to the right hand
    """
    # Read the MIDI file with mido
    mid: MidiFile = MidiFile(midi_path)
    # Validate and ensure tracks are of type MidiTrack
    tracks = cast(List[MidiTrack], mid.tracks)
    for i, track in enumerate(tracks):
      hand: Literal["right", "left"] = "right" if i == 1 else "left"
      self._preprocess_track(track, hand)
    self.events = sorted(self.events, key=lambda x: x.start)

  def _trim_long_notes(self, max_note_length: int) -> None:
    """Trim notes that are longer than max_note_length
    max_note_length: the maximum duration of a note in ticks
    """
    for i in range(len(self.events)):
      self.events[i].trim_note(max_note_length)

  def _fix_sequential_notes(self) -> None:
    def _init_node() -> NoteEvent:
      note = NoteEvent(0, 0, 0)
      note.set_end(0)
      return note

    previous_note_map: Dict[int, NoteEvent] = defaultdict(lambda: _init_node())
    for i in range(len(self.events)):
      current_note = self.events[i]
      if previous_note_map[current_note.note].end > current_note.start:
        previous_note_map[current_note.note].end = current_note.start - 50
      previous_note_map[current_note.note] = current_note

  def get_midi_events(
    self, midi_path: Path, max_note_length: int = 100
  ) -> List[NoteEvent]:
    self.events = []
    self._extract_midi_objects(midi_path)
    self._trim_long_notes(max_note_length=max_note_length)
    self._fix_sequential_notes()
    return self.events

  def get_ticks_per_beat(self, midi_path: Path) -> int:
    mid = MidiFile(midi_path)
    return int(mid.ticks_per_beat)


if __name__ == "__main__":
  preprocessor = MidiPreprocessor()
  source_path = Path(
    os.path.join(
      os.path.dirname(__file__), "../../test/resources/cut_liszt.mid"
    )
  )
  events: List[NoteEvent] = preprocessor.get_midi_events(
    source_path, max_note_length=50
  )
