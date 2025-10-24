from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Note:
    """Represents a musical note in MusicXML."""
    step: Optional[str] = None  # C, D, E, F, G, A, B
    octave: Optional[int] = None
    duration: int = 0
    note_type: Optional[str] = None  # quarter, half, whole, etc.
    voice: Optional[str] = None
    staff: Optional[int] = None
    is_rest: bool = False
    stem: Optional[str] = None
    default_x: Optional[float] = None
    default_y: Optional[float] = None

    def __str__(self):
        if self.is_rest:
            return f"Rest(duration={self.duration}, type={self.note_type})"
        return f"Note({self.step}{self.octave}, duration={self.duration}, type={self.note_type})"


@dataclass
class Measure:
    """Represents a musical measure containing notes."""
    number: int
    notes: list[Note] = field(default_factory=list)
    width: Optional[float] = None

    def __str__(self):
        return f"Measure {self.number}: {len(self.notes)} notes"

    def add_note(self, note: Note):
        self.notes.append(note)


@dataclass
class Part:
    """Represents a musical part containing measures."""
    part_id: str
    name: Optional[str] = None
    measures: list[Measure] = field(default_factory=list)

    def __str__(self):
        return f"Part {self.part_id} ({self.name}): {len(self.measures)} measures"

    def add_measure(self, measure: Measure):
        self.measures.append(measure)


@dataclass
class Score:
    """Represents a complete musical score with metadata and parts."""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    composer: Optional[str] = None
    tempo: Optional[int] = None  # BPM for quarter note
    parts: list[Part] = field(default_factory=list)

    def __str__(self):
        parts_str = f"{len(self.parts)} part(s)"
        return f"Score: {self.title or 'Untitled'} by {self.composer or 'Unknown'} - {parts_str}"

    def add_part(self, part: Part):
        self.parts.append(part)
