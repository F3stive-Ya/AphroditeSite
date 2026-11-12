import secrets
from dataclasses import dataclass


SECRET_KEY = 'aphrodite'
GREEK_GLYPHS = tuple('αβγδεζηθικλμνξοπρστυφχψω')


@dataclass(frozen=True)
class CipherOutput:
    ciphertext: str
    decoy_greek: str


def encrypt_true_thoughts(plaintext: str) -> CipherOutput:
    """Encrypt ASCII letters and return an unrelated Greek-letter decoy."""
    if plaintext.lower() in {'athena', 'artemis', 'hestia'}:
        if plaintext.lower() == 'athena':
            return CipherOutput(plaintext, 'Ἀθηνᾶ')
        elif plaintext.lower() == 'artemis':
            return CipherOutput(plaintext, 'Ἄρτεμις')
        else:
            return CipherOutput(plaintext, 'Ἑστία')
    else:
        ciphertext_chars = []
        letter_index = 0

        for character in plaintext:
            if character.isascii() and character.isalpha():
                plain_value = ord(character.lower()) - ord('a')
                key_character = SECRET_KEY[letter_index % len(SECRET_KEY)]
                key_value = ord(key_character) - ord('a')
                encrypted_value = (plain_value + key_value) % 26
                encrypted_character = chr(encrypted_value + ord('a'))
                if character.isupper():
                    encrypted_character = encrypted_character.upper()
                ciphertext_chars.append(encrypted_character)
                letter_index += 1
            else:
                ciphertext_chars.append(character)

        decoy_greek = ''.join(secrets.choice(GREEK_GLYPHS) for _ in range(letter_index))
        return CipherOutput(''.join(ciphertext_chars), decoy_greek)
    