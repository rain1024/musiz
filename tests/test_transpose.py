import pytest
from src.abc_notation import ABCNotation
from src.transformations import transpose


@pytest.fixture
def original_score():
    """Load the original ode_to_joy.abc score."""
    return ABCNotation.read("ode_to_joy.abc")


def test_transpose_up_2_semitones(original_score):
    """Test transposing up 2 semitones (whole step)."""
    transposed = transpose(original_score, 2)

    # Check that score metadata is preserved
    assert transposed.title == original_score.title
    assert transposed.composer == original_score.composer
    assert transposed.tempo == original_score.tempo

    # Check first measure notes
    # Original: F F G A (in D major, so F# F# G A)
    # Up 2 semitones: G# G# A B -> G G A B
    first_measure = transposed.parts[0].measures[0]
    assert len(first_measure.notes) == 4
    assert first_measure.notes[0].step == "G"
    assert first_measure.notes[0].octave == 4
    assert first_measure.notes[1].step == "G"
    assert first_measure.notes[2].step == "A"
    assert first_measure.notes[3].step == "B"


def test_transpose_down_5_semitones(original_score):
    """Test transposing down 5 semitones (perfect fourth)."""
    transposed = transpose(original_score, -5)

    # Check that score metadata is preserved
    assert transposed.title == original_score.title

    # Check first measure notes
    # Original: F F G A (in D major)
    # Down 5 semitones: C C D E
    first_measure = transposed.parts[0].measures[0]
    assert len(first_measure.notes) == 4
    assert first_measure.notes[0].step == "C"
    assert first_measure.notes[0].octave == 4
    assert first_measure.notes[1].step == "C"
    assert first_measure.notes[2].step == "D"
    assert first_measure.notes[3].step == "E"


def test_transpose_zero_semitones(original_score):
    """Test that transposing by 0 semitones produces identical notes."""
    transposed = transpose(original_score, 0)

    # Should have same notes
    original_first = original_score.parts[0].measures[0]
    transposed_first = transposed.parts[0].measures[0]

    assert len(original_first.notes) == len(transposed_first.notes)
    for orig, trans in zip(original_first.notes, transposed_first.notes):
        assert orig.step == trans.step
        assert orig.octave == trans.octave


def test_transpose_preserves_duration(original_score):
    """Test that transposition preserves note durations."""
    transposed = transpose(original_score, 3)

    # Check that all notes have same durations
    for orig_measure, trans_measure in zip(
        original_score.parts[0].measures,
        transposed.parts[0].measures
    ):
        assert len(orig_measure.notes) == len(trans_measure.notes)
        for orig_note, trans_note in zip(orig_measure.notes, trans_measure.notes):
            assert orig_note.duration == trans_note.duration
            assert orig_note.note_type == trans_note.note_type


def test_transpose_octave_change(original_score):
    """Test that transposing by 12 semitones changes octave."""
    transposed = transpose(original_score, 12)

    # First note should be F5 instead of F4
    first_note = transposed.parts[0].measures[0].notes[0]
    original_first_note = original_score.parts[0].measures[0].notes[0]

    assert first_note.step == original_first_note.step
    assert first_note.octave == original_first_note.octave + 1
