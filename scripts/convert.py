import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.musicxml import MusicXML
from src.abc_notation import ABCNotation


def main():
    # Read ABC file
    print("Reading ode_to_joy.abc...")
    abc_score = ABCNotation.read("ode_to_joy.abc")
    print(f"Loaded: {abc_score}")

    # Write to MusicXML
    print("\nConverting to MusicXML...")
    MusicXML.write(abc_score, "ode_to_joy.musicxml")
    print("✓ Successfully written to ode_to_joy.musicxml")


if __name__ == "__main__":
    main()
