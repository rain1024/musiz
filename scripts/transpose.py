#!/usr/bin/env python3
"""CLI tool for transposing music files."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.abc_notation import ABCNotation
from src.musicxml import MusicXML
from src.transformations import transpose


def detect_format(filepath: str) -> str:
    """Detect music file format from extension."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == '.abc':
        return 'abc'
    elif suffix in ['.xml', '.musicxml']:
        return 'musicxml'
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def read_score(filepath: str):
    """Read a music score from file."""
    format_type = detect_format(filepath)

    if format_type == 'abc':
        return ABCNotation.read(filepath)
    elif format_type == 'musicxml':
        return MusicXML.read(filepath)


def write_score(score, filepath: str, key: str = None):
    """Write a music score to file."""
    format_type = detect_format(filepath)

    if format_type == 'abc':
        if key is None:
            key = 'C'
        ABCNotation.write(score, filepath, key=key)
    elif format_type == 'musicxml':
        MusicXML.write(score, filepath)


def main():
    parser = argparse.ArgumentParser(
        description='Transpose music files by semitones',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transpose up a whole step (2 semitones)
  %(prog)s song.abc -s 2 -o song_transposed.abc

  # Transpose down a perfect fifth (7 semitones)
  %(prog)s song.musicxml -s -7 -o song_lower.musicxml

  # Transpose and change key signature (ABC only)
  %(prog)s song.abc -s 2 -o song_d.abc -k D
        """
    )

    parser.add_argument(
        'input',
        help='Input music file (.abc or .musicxml)'
    )

    parser.add_argument(
        '-s', '--semitones',
        type=int,
        required=True,
        help='Number of semitones to transpose (positive = up, negative = down)'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file path'
    )

    parser.add_argument(
        '-k', '--key',
        default=None,
        help='Key signature for output (ABC format only, e.g., C, D, Dm, G)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print verbose output'
    )

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        # Read input file
        if args.verbose:
            print(f"Reading {args.input}...")
        score = read_score(args.input)

        if args.verbose:
            print(f"Loaded: {score}")
            print(f"Transposing by {args.semitones} semitones...")

        # Transpose
        transposed = transpose(score, args.semitones)

        # Write output file
        if args.verbose:
            print(f"Writing to {args.output}...")
        write_score(transposed, args.output, key=args.key)

        print(f"✓ Successfully transposed {args.input} by {args.semitones} semitones")
        print(f"  Output: {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
