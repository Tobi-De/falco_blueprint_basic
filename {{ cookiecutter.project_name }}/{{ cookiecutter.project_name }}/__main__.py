import os
import sys
import multiprocessing
import subprocess
from pathlib import Path
from contextlib import suppress


def main():
    current_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(current_path))
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", f"{{ cookiecutter.project_name }}.settings"
    )

    commands = {
        "manage": run_manage,
        "setup": run_setup,
        "server": run_server,
        "workers": run_workers,
    }
    command_key = sys.argv[1] if len(sys.argv) > 1 else None
    run_func = commands.get(command_key) or "server"  # run server by default

    run_func(sys.argv)


def run_setup(_):
    """
    Run project setup tasks, applying migrations, creating a superuser if needed etc.
    """
    from django.core.management import execute_from_command_line
    from django.core.management.base import CommandError

    execute_from_command_line(["manage", "litestream", "init"])
    execute_from_command_line(
        [
            "manage",
            "litestream",
            "restore",
            "default",
            "-if-replica-exists",
            "-if-db-not-exists",
        ]
    )
    execute_from_command_line(["manage", "migrate"])
    execute_from_command_line(["manage", "setup_periodic_tasks"])
    with suppress(CommandError):
        execute_from_command_line(
            ["manage", "createsuperuser", "--noinput", "--traceback"]
        )


def run_server(_):
    """
    Run Granian, the WSGI server. If using SQLite as the database, Litestream is used for replication.
    """
    bin_dir = Path(sys.executable).parent
    workers = multiprocessing.cpu_count() * 2 + 1
    granian_args = [
        "--workers",
        str(workers),
        "--interface",
        "wsgi",
        "--port",
        "8000",
        "--host",
        "0.0.0.0",
        ".wsgi:application",
    ]

    if "sqlite" in os.getenv("DATABASE_URL", ""):
        # Construct the Granian command as a single string for Litestream
        litestream_executable = bin_dir / "litestream"
        execute_granian = f"granian {' '.join(granian_args)}"
        command = [str(litestream_executable), "replicate", "-exec", execute_granian]
    else:
        granian_executable = bin_dir / "granian"
        command = [str(granian_executable)] + granian_args

    subprocess.run(command, check=True)


def run_workers(argv):
    """
    Run the Django Q cluster for handling background tasks.
    """
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage", "qcluster", *argv[2:]])


def run_manage(argv):
    """
    Run Django's manage.py commands.
    """
    from django.core.management import execute_from_command_line

    execute_from_command_line(argv[1:])


if __name__ == "__main__":
    main()
