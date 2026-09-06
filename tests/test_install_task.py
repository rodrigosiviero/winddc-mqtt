from pathlib import Path


SCRIPT = Path("scripts/install-user-task.ps1")


def test_task_runs_the_repository_virtualenv_without_cmd() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert '.venv\\Scripts\\pythonw.exe' in script
    assert 'start.py' in script
    assert 'run_winddc.bat' not in script
