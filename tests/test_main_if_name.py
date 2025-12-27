import pytest
from src.main import main
from unittest.mock import patch, MagicMock
import runpy
import sys

def test_if_name_main(capsys):
    # We want to simulate python -m src.main --help
    with patch("sys.argv", ["src/main.py", "--help"]):
        with pytest.raises(SystemExit):
             runpy.run_module("src.main", run_name="__main__")

    captured = capsys.readouterr()
    assert "eDNA Literature Miner" in captured.out
