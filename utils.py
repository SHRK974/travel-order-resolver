import os

from constants import INPUT_READLINE, INPUT_FILE, INPUT_SPEECH, FILE_INPUT_LOCATION, ERROR_NOT_FRENCH

from langdetect import detect

def check_french(text: str) -> bool:
    """Check if text is in French.

    Args:
        text (str): text to check

    Returns:
        bool: True if text is in French, False otherwise
    """
    is_french = detect(text) == 'fr'
    if not is_french:
        raise Exception(ERROR_NOT_FRENCH)
    return is_french

# Utility functions
def handle_input_type_selection() -> int:
    """Ask user to select input type.

    Returns:
        int: input type (0: readline, 1: csv, 2: microphone)
    """
    input_type = None
    while input_type not in [INPUT_READLINE, INPUT_FILE, INPUT_SPEECH]:
        input_type = int(input("Choisissez votre source d'entrée: {0: readline, 1: csv, 2: microphone} "))
    return input_type

def handle_input_type_csv(filename: str) -> str:
    # Find file in input folder
    filepath = FILE_INPUT_LOCATION + filename + '.csv'
    # Check if file exists
    if not os.path.isfile(filepath):
        print(f"Le fichier {filepath} n'existe pas.")
        exit()
    # Return file path
    return filepath

def print_decorated(text = None, decoration='-', length=25):
    """Print text with a decoration on each side."""
    print()
    print(decoration * length)
    if isinstance(text, str):
        print(text)
    print(decoration * length)
    print()
