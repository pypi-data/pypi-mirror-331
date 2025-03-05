# Morse Tub

A package for Morse code conversions and sound playback (Windows-only).

## Installation

```bash
pip install git+https://github.com/rushiharkal1/morse_tub.git
```

## Usage

```python
from morse_code import text_to_morse_code, morse_code_to_text, play_morse_code

# Convert text to Morse code
morse_code = text_to_morse_code("Hello World")
print(morse_code)

# Convert Morse code to text
text = morse_code_to_text(morse_code)
print(text)

# Play Morse code as sound
play_morse_code(morse_code)
```

**Note**: This package currently supports only Windows due to the use of the winsound module. Cross-platform support is planned for future updates.