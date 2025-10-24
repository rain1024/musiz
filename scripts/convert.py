#!/usr/bin/env python3
"""CLI tool for converting between ABC notation and MusicXML formats."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.musicxml import MusicXML
from src.abc_notation import ABCNotation


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


def main():
    parser = argparse.ArgumentParser(
        description='Convert between ABC notation and MusicXML formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert ABC to MusicXML
  %(prog)s ode_to_joy.abc -o ode_to_joy.musicxml

  # Convert MusicXML to ABC
  %(prog)s song.musicxml -o song.abc -k D

  # Verbose output
  %(prog)s input.abc -o output.musicxml -v
        """
    )

    parser.add_argument(
        'input',
        help='Input music file (.abc or .musicxml)'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file path'
    )

    parser.add_argument(
        '-k', '--key',
        default='C',
        help='Key signature for ABC output (default: C, e.g., D, Dm, G)'
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
        # Detect input and output formats
        input_format = detect_format(args.input)
        output_format = detect_format(args.output)

        # Read input file
        if args.verbose:
            print(f"Reading {args.input} ({input_format})...")

        if input_format == 'abc':
            score = ABCNotation.read(args.input)
        else:
            score = MusicXML.read(args.input)

        if args.verbose:
            print(f"Loaded: {score}")
            print(f"Converting to {output_format}...")

        # Write output file
        if output_format == 'abc':
            ABCNotation.write(score, args.output, key=args.key)
        else:
            MusicXML.write(score, args.output)

        print(f"✓ Successfully converted {args.input} to {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
