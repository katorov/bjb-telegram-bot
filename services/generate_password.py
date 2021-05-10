import random

NUMBERS = list('1234567890')
LOWERCASE_LETTERS = list('abcdefghigklmnopqrstuvyxwz')
UPPERCASE_LETTERS = list('ABCDEFGHIGKLMNOPQRSTUVYXWZ')
ALL_LETTERS = LOWERCASE_LETTERS + UPPERCASE_LETTERS
SPECIAL_SYMBOLS = list('.@:')


def generate_random_password(count_letters=4, count_numbers=4, count_specials=1):
    """Генерировать рандомный пароль"""

    password = ''
    for _ in range(count_letters):
        password += random.choice(ALL_LETTERS)
    for _ in range(count_numbers):
        password += random.choice(NUMBERS)
    for _ in range(count_specials):
        password += random.choice(SPECIAL_SYMBOLS)

    password = list(password)
    random.shuffle(password)
    return ''.join(password)
