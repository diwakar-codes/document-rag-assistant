from app.utils.text_cleaner import TextCleaner


def test_multiple_spaces():
    text = "Hello     World"
    assert TextCleaner.clean(text) == "Hello World"


def test_multiple_blank_lines():
    text = "Hello\n\n\n\nWorld"
    assert TextCleaner.clean(text) == "Hello\n\nWorld"


def test_tabs():
    text = "Hello\t\tWorld"
    assert TextCleaner.clean(text) == "Hello World"


def test_empty_string():
    assert TextCleaner.clean("") == ""