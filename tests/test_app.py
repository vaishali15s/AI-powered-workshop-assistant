import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "510_ABW.py"
SPEC = importlib.util.spec_from_file_location("workshop_assistant", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_should_launch_streamlit_when_context_present(monkeypatch):
    monkeypatch.setattr(MODULE, "get_script_run_ctx", lambda: object())

    assert MODULE.should_launch_streamlit() is True


def test_should_not_launch_streamlit_without_context(monkeypatch):
    monkeypatch.setattr(MODULE, "get_script_run_ctx", lambda: None)

    assert MODULE.should_launch_streamlit() is False
