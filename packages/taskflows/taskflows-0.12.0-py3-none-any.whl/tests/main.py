import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

import taskflows

if __name__ == "__main__":

    args = [
        "--sw",
        "-s",
        "-vv",
        "--pg-url",
        "postgresql+psycopg://dank:JoeyRiley01@0.0.0.0:5434/trading",
        # "postgresql://test:test@postgres/test",
    ]

    files = [
        "test_service.py",
        "test_task_logger.py",
        "test_task.py",
        "test_docker.py",
    ]
    files = [f"/home/dan/repos-dev/taskflows/tests/{f}" for f in files]

    for f in files:
        pytest.main(args + [f])
