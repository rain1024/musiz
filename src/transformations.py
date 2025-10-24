from src.data_classes import Score, Part, Measure, Note


class MusicTransformer:
    """Music transformation utilities."""

    # Chromatic scale for transposition
    CHROMATIC_SCALE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

    # Semitone intervals between notes (C to next note)
    SEMITONE_INTERVALS = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }

    @staticmethod
    def transpose(score: Score, semitones: int) -> Score:
        """
        Transpose a score by a given number of semitones.

        Args:
            score: The original score
            semitones: Number of semitones to transpose (positive = up, negative = down)

        Returns:
            A new transposed Score object
        """
        # Create a new score with copied metadata
        transposed_score = Score(
            title=score.title,
            subtitle=score.subtitle,
            composer=score.composer,
            tempo=score.tempo
        )

        # Transpose each part
        for part in score.parts:
            transposed_part = Part(
                part_id=part.part_id,
                name=part.name
            )

            # Transpose each measure
            for measure in part.measures:
                transposed_measure = Measure(
                    number=measure.number,
                    width=measure.width
                )

                # Transpose each note
                for note in measure.notes:
                    transposed_note = MusicTransformer._transpose_note(note, semitones)
                    transposed_measure.add_note(transposed_note)

                transposed_part.add_measure(transposed_measure)

            transposed_score.add_part(transposed_part)

        return transposed_score

    @staticmethod
    def _transpose_note(note: Note, semitones: int) -> Note:
        """Transpose a single note by semitones."""
        # If it's a rest, just copy it
        if note.is_rest:
            return Note(
                step=note.step,
                octave=note.octave,
                duration=note.duration,
                note_type=note.note_type,
                voice=note.voice,
                staff=note.staff,
                is_rest=True,
                stem=note.stem,
                default_x=note.default_x,
                default_y=note.default_y
            )

        # Get current note position in chromatic scale
        if not note.step:
            # Return as-is if no step defined
            return note

        # Calculate new position
        current_octave = note.octave or 4

        # Transpose by semitones
        # Convert to absolute semitone position
        absolute_position = current_octave * 12 + MusicTransformer.SEMITONE_INTERVALS[note.step]
        new_position = absolute_position + semitones

        # Convert back to note + octave
        new_octave = new_position // 12
        new_semitone = new_position % 12

        # Find the closest note in the scale
        # Map semitone back to note name
        semitone_to_note = {
            0: 'C', 1: 'C', 2: 'D', 3: 'D', 4: 'E', 5: 'F',
            6: 'F', 7: 'G', 8: 'G', 9: 'A', 10: 'A', 11: 'B'
        }
        new_step = semitone_to_note[new_semitone]

        return Note(
            step=new_step,
            octave=new_octave,
            duration=note.duration,
            note_type=note.note_type,
            voice=note.voice,
            staff=note.staff,
            is_rest=False,
            stem=note.stem,
            default_x=note.default_x,
            default_y=note.default_y
        )


def transpose(score: Score, semitones: int) -> Score:
    """
    Transpose a musical score by a given number of semitones.

    Args:
        score: The score to transpose
        semitones: Number of semitones to transpose (positive = up, negative = down)

    Returns:
        A new transposed Score

    Examples:
        # Transpose up a whole step (2 semitones)
        transposed = transpose(score, 2)

        # Transpose down a perfect fifth (7 semitones)
        transposed = transpose(score, -7)
    """
    return MusicTransformer.transpose(score, semitones)
