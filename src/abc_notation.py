import re
from src.data_classes import Note, Measure, Part, Score


class ABCNotation:
    """Read and write ABC notation files."""

    # ABC note duration mapping (relative to L: unit)
    NOTE_PATTERN = re.compile(r"([_=^]?)([A-Ga-g],*'*)(\d*/?(\d*))")

    @staticmethod
    def read(filepath: str) -> Score:
        """Parse an ABC file and return a Score object."""
        with open(filepath, 'r') as f:
            lines = f.readlines()

        score = Score()

        # Parse header fields
        metadata = {}
        music_lines = []
        in_header = True

        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):  # Skip empty lines and comments
                continue

            # Header field (X:, T:, C:, M:, L:, K:)
            if ':' in line and in_header:
                field_type = line[0]
                field_value = line[2:].strip()
                metadata[field_type] = field_value

                # K: field marks end of header
                if field_type == 'K':
                    in_header = False
            else:
                # Music notation
                music_lines.append(line)

        # Set score metadata
        score.title = metadata.get('T')
        score.composer = metadata.get('C')

        # Parse tempo (Q: field)
        tempo_str = metadata.get('Q')
        if tempo_str:
            score.tempo = ABCNotation._parse_tempo(tempo_str)

        # Parse music
        part = Part(part_id="P1", name=metadata.get('T'))

        # Get unit note length (default 1/8)
        unit_length = ABCNotation._parse_unit_length(metadata.get('L', '1/8'))

        # Parse measures from music lines
        measure_num = 1
        for line in music_lines:
            # Split by bar lines
            measures_text = line.split('|')

            for measure_text in measures_text:
                measure_text = measure_text.strip()
                if not measure_text:
                    continue

                measure = Measure(number=measure_num)

                # Parse notes in the measure
                notes = ABCNotation._parse_notes(measure_text, unit_length)
                for note in notes:
                    measure.add_note(note)

                if measure.notes:  # Only add non-empty measures
                    part.add_measure(measure)
                    measure_num += 1

        score.add_part(part)
        return score

    @staticmethod
    def write(score: Score, filepath: str, key: str = "C") -> None:
        """
        Write a Score object to an ABC file.

        Args:
            score: The score to write
            filepath: Output file path
            key: Musical key (e.g., "C", "D", "Dm", "G")
        """
        lines = []

        # Header fields
        lines.append("X:1")
        if score.title:
            lines.append(f"T:{score.title}")
        if score.composer:
            lines.append(f"C:{score.composer}")
        lines.append("M:4/4")
        lines.append("L:1/4")
        if score.tempo:
            lines.append(f"Q:1/4={score.tempo}")
        lines.append(f"K:{key}")

        # Music notation
        if score.parts:
            part = score.parts[0]  # Take first part

            measure_count = 0
            music_line = []

            for measure in part.measures:
                # Convert notes to ABC notation
                note_strs = []
                for note in measure.notes:
                    note_str = ABCNotation._note_to_abc(note)
                    if note_str:
                        note_strs.append(note_str)

                if note_strs:
                    music_line.append(" ".join(note_strs))
                    measure_count += 1

                    # Add bar line and newline every 4 measures
                    if measure_count % 4 == 0:
                        lines.append(" | ".join(music_line) + " |")
                        music_line = []

            # Add remaining measures
            if music_line:
                lines.append(" | ".join(music_line) + " ||")

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

    @staticmethod
    def _parse_unit_length(length_str: str) -> float:
        """Parse unit length like '1/8' to float (0.125)."""
        if '/' in length_str:
            num, denom = length_str.split('/')
            return int(num) / int(denom)
        return float(length_str)

    @staticmethod
    def _parse_tempo(tempo_str: str) -> int:
        """Parse tempo like '1/4=108' to BPM value (108)."""
        # Format: note_value=bpm (e.g., "1/4=108")
        if '=' in tempo_str:
            parts = tempo_str.split('=')
            if len(parts) == 2:
                try:
                    return int(parts[1].strip())
                except ValueError:
                    pass
        return 120  # default tempo

    @staticmethod
    def _parse_notes(measure_text: str, unit_length: float) -> list[Note]:
        """Parse notes from a measure text."""
        notes = []

        # Remove extra whitespace
        measure_text = measure_text.strip()

        i = 0
        while i < len(measure_text):
            char = measure_text[i]

            # Skip whitespace
            if char.isspace():
                i += 1
                continue

            # Parse note
            if char in 'ABCDEFGabcdefg_=^':
                note_str, length = ABCNotation._extract_note(measure_text[i:])
                i += length

                if note_str:
                    note = ABCNotation._parse_single_note(note_str, unit_length)
                    if note:
                        notes.append(note)
            else:
                i += 1

        return notes

    @staticmethod
    def _extract_note(text: str) -> tuple[str, int]:
        """Extract a single note string and its length in characters."""
        match = ABCNotation.NOTE_PATTERN.match(text)
        if match:
            return match.group(0), len(match.group(0))

        # Simple fallback for basic notes
        length = 1
        # Check for duration number
        if length < len(text) and text[length].isdigit():
            while length < len(text) and (text[length].isdigit() or text[length] == '/'):
                length += 1

        return text[:length], length

    @staticmethod
    def _parse_single_note(note_str: str, unit_length: float) -> Note | None:
        """Parse a single ABC note string into a Note object."""
        # Handle accidentals (^, _, =)
        idx = 0
        if note_str[0] in '^_=':
            # accidental = note_str[0]  # TODO: Handle accidentals in future
            idx = 1

        # Get note letter
        if idx >= len(note_str):
            return None

        note_letter = note_str[idx]
        idx += 1

        # Determine octave from case and octave markers (, and ')
        # Lowercase = octave 5, uppercase = octave 4
        # Each , lowers octave, each ' raises octave
        if note_letter.islower():
            octave = 5
            step = note_letter.upper()
        else:
            octave = 4
            step = note_letter

        # Handle octave modifiers
        while idx < len(note_str) and note_str[idx] in ",'":
            if note_str[idx] == ',':
                octave -= 1
            elif note_str[idx] == "'":
                octave += 1
            idx += 1

        # Parse duration (default is 1 unit)
        duration_multiplier = 1.0

        if idx < len(note_str):
            duration_str = note_str[idx:]

            if duration_str == '':
                duration_multiplier = 1.0
            elif duration_str[0] == '/':
                # /2 means half, /4 means quarter, / alone means /2
                if len(duration_str) == 1:
                    duration_multiplier = 0.5
                else:
                    try:
                        duration_multiplier = 1.0 / int(duration_str[1:])
                    except ValueError:
                        duration_multiplier = 0.5
            elif duration_str[0].isdigit():
                # 2 means double, 3 means triple, etc.
                try:
                    # Handle cases like "3/2"
                    if '/' in duration_str:
                        num, denom = duration_str.split('/')
                        duration_multiplier = int(num) / int(denom)
                    else:
                        duration_multiplier = int(duration_str)
                except ValueError:
                    duration_multiplier = 1.0

        # Calculate actual duration
        actual_duration = unit_length * duration_multiplier

        # Map to note type (approximation)
        note_type = ABCNotation._duration_to_type(actual_duration)

        # Convert to divisions (use 8 divisions per whole note for better precision)
        # This handles dotted notes and divisions better
        duration_divisions = round(actual_duration * 8)

        return Note(
            step=step,
            octave=octave,
            duration=duration_divisions,
            note_type=note_type,
            is_rest=False
        )

    @staticmethod
    def _duration_to_type(duration: float) -> str:
        """Convert duration to note type."""
        if duration >= 1.0:
            return "whole"
        elif duration >= 0.5:
            return "half"
        elif duration >= 0.25:
            return "quarter"
        elif duration >= 0.125:
            return "eighth"
        else:
            return "16th"

    @staticmethod
    def _note_to_abc(note: Note) -> str:
        """Convert a Note object to ABC notation."""
        if note.is_rest:
            return ABCNotation._duration_to_abc_suffix(note.duration)

        if not note.step:
            return ""

        # Convert note letter and octave to ABC notation
        # Octave 4 = uppercase, octave 5 = lowercase
        # ABC notation: C,, C, C c c' c''
        step = note.step
        octave = note.octave or 4

        if octave == 4:
            abc_note = step.upper()
        elif octave == 5:
            abc_note = step.lower()
        elif octave == 3:
            abc_note = step.upper() + ","
        elif octave == 6:
            abc_note = step.lower() + "'"
        elif octave == 2:
            abc_note = step.upper() + ",,"
        else:
            abc_note = step.upper()

        # Add duration suffix
        duration_suffix = ABCNotation._duration_to_abc_suffix(note.duration)

        return abc_note + duration_suffix

    @staticmethod
    def _duration_to_abc_suffix(duration: int) -> str:
        """
        Convert duration (in divisions) to ABC duration suffix.
        With divisions=2, quarter note = 2, eighth = 1, half = 4, etc.
        """
        # Map duration to ABC suffix
        # quarter note (2) = no suffix
        # eighth (1) = /
        # half (4) = 2
        # dotted quarter (3) = 3/2
        # whole (8) = 4

        if duration == 2:  # quarter
            return ""
        elif duration == 1:  # eighth
            return "/"
        elif duration == 4:  # half
            return "2"
        elif duration == 3:  # dotted quarter
            return "3/2"
        elif duration == 8:  # whole
            return "4"
        elif duration == 6:  # dotted half
            return "3"
        else:
            # Generic handling
            if duration < 2:
                return f"/{int(2/duration)}"
            else:
                return str(int(duration / 2))
