import winsound
import time

# Morse Code dictionary "a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0 , . ? / - ( ) ' " & ; _ + = @"
MORSE_CODE_DICT = {
    # Alphabets
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.',
    'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-',
    'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    # Numbers
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', 
    '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    # Symbols
    ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', 
    '(': '-.--.', ')': '-.--.-', "'": '.----.', '"': '.-..-.', '&': '.-...', ';': '-.-.-.', 
    '_': '..--.-', '+': '.-.-.', '=': '-...-', '@': '.--.-.'
}


# Function to convert text to morse code
def text_to_morse_code(text):
    morse_code = ''
    for letter in text.upper():
        if letter in MORSE_CODE_DICT:
            morse_code += MORSE_CODE_DICT[letter] + ' '  # Separate letters with a space
        else:
            morse_code += ' / '  # Separate words with '/'
    return morse_code


# Function to convert morse code to text
def morse_code_to_text(morse_code):
    # Reverse the MORSE_CODE_DICT to map Morse code to characters
    REVERSE_MORSE_CODE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}
    text = ''
    morse_words = morse_code.strip().split(' / ')  # Split by ' / ' for words
    for morse_word in morse_words:
        morse_letters = morse_word.split(' ')  # Split by ' ' for letters
        for code in morse_letters:
            if code in REVERSE_MORSE_CODE_DICT:
                text += REVERSE_MORSE_CODE_DICT[code]
        text += ' '  # Add space between words
    return text.strip()


# Function to play the morse code as sound
def play_morse_code(morse_code):
    # I've added comments to explain the Morse code timing and separation rules:
    # Dot (.) = 1 unit of time (50 ms)
    # Dash (-) = 3 units of time (150 ms)
    # Pause between symbols in a letter = 1 unit of time (50 ms)
    # Pause between letters in a word = 3 units of time (150 ms)
    # Pause between words = 7 units of time (350 ms)
    for symbol in morse_code:
        if symbol == '.':
            winsound.Beep(1000, 50)   # Dot: Frequency 1000 Hz, duration 50 ms
            time.sleep(0.05)          # Pause between symbols in a letter: 1 unit of time (50 ms)
        elif symbol == '-':
            winsound.Beep(1000, 150)  # Dash: Frequency 1000 Hz, duration 150 ms
            time.sleep(0.05)          # Pause between symbols in a letter: 1 unit of time (50 ms)
        elif symbol == ' ':
            time.sleep(0.15)          # Pause between letters: 3 units of time (150 ms)
        elif symbol == '/':
            time.sleep(0.35)          # Pause between words: 7 units of time (350 ms)
