import subprocess
import sys

import pytest


@pytest.fixture
def run(tmp_path):
    def _run(*args, cwd=None):
        proc = subprocess.run(
            [sys.executable, "-m", "agentperm", *args],
            cwd=cwd or tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return proc

    return _run


COMMANDS = [("check", "build-bot", "read", "repo/app"), ("expired",)]


def combined(proc):
    return proc.stdout + proc.stderr
