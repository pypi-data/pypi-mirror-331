import argparse
import sys
from pathlib import Path
from .lexer import Lexer
from .parser import Parser
from .midi_generator import MIDIGenerator


def main():
    arg_parser = argparse.ArgumentParser(
        description="MidiScript - A musical programming language"
    )
    arg_parser.add_argument("input", help="Input MidiScript file")
    arg_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output MIDI file (default: <input_file>.mid)",
        default=None,
    )

    args = arg_parser.parse_args()

    # Read input file
    try:
        with open(args.input, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.input}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Set output filename
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = str(input_path.with_suffix(".mid"))

    try:
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # Parse
        parser = Parser(tokens)
        program = parser.parse()

        # Generate MIDI
        generator = MIDIGenerator()
        midi_data = generator.generate(program)

        # Write output file
        with open(output_file, "wb") as f:
            f.write(midi_data)

        print(f"Successfully created MIDI file: {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
