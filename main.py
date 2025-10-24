from src.musicxml import MusicXML
from src.abc_notation import ABCNotation


def main():
    # Parse the ABC file
    print("=== Parsing ABC file ===")
    abc_score = ABCNotation.read("ode_to_joy.abc")

    print(f"Loaded: {abc_score}")
    print("\nFirst 4 measures:")
    for part in abc_score.parts:
        print(f"  {part}")
        for measure in part.measures[:4]:  # Show first 4 measures
            print(f"    {measure}")
            for note in measure.notes:
                print(f"      {note}")

    # Convert ABC to MusicXML
    print("\n=== Converting to MusicXML ===")
    output_file = "ode_to_joy.musicxml"
    MusicXML.write(abc_score, output_file)
    print(f"Written to {output_file}")

    # Read it back to verify
    print("\n=== Reading back the MusicXML file ===")
    converted_score = MusicXML.read(output_file)
    print(f"Loaded: {converted_score}")
    print("\nFirst 4 measures:")
    for part in converted_score.parts:
        print(f"  {part}")
        for measure in part.measures[:4]:
            print(f"    {measure}")
            for note in measure.notes:
                print(f"      {note}")


if __name__ == "__main__":
    main()
