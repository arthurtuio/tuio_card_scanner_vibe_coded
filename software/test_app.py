from app import extract_number, clean_name

def test_number():
    assert extract_number('025/198') == '025'
    assert extract_number('SVP 123 / 150') == 'SVP123'
    assert extract_number('No number in text') is None

def test_name():
    assert clean_name('BASIC Pokémon\nPikachu\nHP 60') == 'Pikachu'

if __name__ == '__main__':
    test_number(); test_name();print('Self tests passed')
