import random

# taken from
# https://stackoverflow.com/questions/1891404/how-do-you-create-an-english-like-word


vowels_pairs = (("a", 78),
                ("e", 110),
                ("i", 86),
                ("o", 61),
                ("u", 33))
vowels_w = [x[1] for x in vowels_pairs]
vowels_l = [x[0] for x in vowels_pairs]

consonants_pairs = (('b', 20),
                    ('c', 40),
                    ('d', 38),
                    ('f', 14),
                    ('g', 30),
                    ('h', 23),
                    ('j', 2),
                    ('k', 9),
                    ('l', 53),
                    ('m', 27),
                    ('n', 72),
                    ('p', 28),
                    ('q', 2),
                    ('r', 73),
                    ('s', 87),
                    ('t', 67),
                    ('v', 10),
                    ('w', 9),
                    ('x', 3),
                    ('y', 16),
                    ('z', 4))
consonants_w = [x[1] for x in consonants_pairs]
consonants_l = [x[0] for x in consonants_pairs]


def _vowel():
    return random.choices(vowels_l, vowels_w)[0]


def _consonant():
    return random.choices(consonants_l, consonants_w)[0]


def _cv():
    return _consonant() + _vowel()


def _cvc():
    return _cv() + _consonant()


def _syllable():
    return random.choice([_vowel, _cv, _cvc])()


def create_fake_word_len(a, b, min_len: int = 0, max_len: int = 0):
    """ This function generates a fake word by creating between two and three
        random syllables and then joining them together.
    """
    attempts = 100
    for i in range(attempts):
        word = create_fake_word(a, b)
        if min_len > 0 and len(word) < min_len:
            continue
        if max_len > 0 and len(word) > max_len:
            continue
        return word
    else:
        raise RuntimeError(f'Could not generate required fake world with {attempts} attempts.')


def create_fake_word(a, b):
    syllables = []
    for x in range(random.randint(a, b)):
        syllables.append(_syllable())
    return "".join(syllables)
