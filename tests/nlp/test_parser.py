import os

def test_parser_exists():
    assert os.path.exists(
        "src/nlp/parser.py"
    )

def test_output_folder():
    assert os.path.exists(
        "output"
    )