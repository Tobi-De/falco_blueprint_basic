def main() -> None:
    import os
    import sys
    from pathlib import Path

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "{{ cookiecutter.project_name }}.settings"
    )
    current_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(current_path))

    run_func = None
    if len(sys.argv) > 1:
        run_func = COMMANDS.get(sys.argv[1])

    if run_func:
        run_func(sys.argv)
    else:
        run_gunicorn(sys.argv)


def _get_sqlite_db_path() -> str:
    """Return the path to the SQLite database file."""
    from django.conf import settings

    db_settings = settings.DATABASES.get("default")
    if db_settings and db_settings.get("ENGINE") == "django.db.backends.sqlite3":
        return db_settings["NAME"]
    exit("No SQLite database found in settings")


def run_setup(_):
    """Run some project setup tasks"""
    import os
    import subprocess
    from pathlib import Path
    from django.core.management import execute_from_command_line
    from django.core.management.base import CommandError
    from contextlib import suppress

    db_path = _get_sqlite_db_path()
    # The Litestream configuration uses this environment variable, so it needs
    # to be injected into every function that runs the Litestream command.
    os.environ.setdefault("DATABASE_PATH", db_path)

    replica_url = os.getenv("REPLICA_URL")

    if not replica_url:
        exit("REPLICA_URL environment variable not set")

    if Path(db_path).exists():
        print("Database already exists, skipping restore")
    else:
        print("No database found, restoring from replica if exists")
        subprocess.run(
            ["litestream", "restore", "-if-replica-exists", "-o", db_path, replica_url]
        )

    execute_from_command_line(["manage", "migrate"])
    execute_from_command_line(["manage", "setup_periodic_tasks"])

    with suppress(CommandError):
        execute_from_command_line(
            ["manage", "createsuperuser", "--noinput", "--traceback"]
        )


def run_gunicorn(argv: list) -> None:
    """
    Run gunicorn the wsgi server.
    https://docs.gunicorn.org/en/stable/settings.html
    https://adamj.eu/tech/2021/12/29/set-up-a-gunicorn-configuration-file-and-test-it/
    """
    import multiprocessing
    from gunicorn.app import wsgiapp

    workers = multiprocessing.cpu_count() * 2 + 1
    gunicorn_args = [
        "{{ cookiecutter.project_name }}.wsgi:application",
        "--bind",
        "127.0.0.1:8000",
        # "unix:/run/{{ cookiecutter.project_name }}.gunicorn.sock", # uncomment this line and comment the line above to use a socket file
        "--max-requests",
        "1000",
        "--max-requests-jitter",
        "50",
        "--workers",
        str(workers),
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
    ]
    argv.extend(gunicorn_args)
    wsgiapp.run()


def run_litestream(argv: list) -> None:
    """
    Run Litestream the SQLite replication tool.
    https://litestream.io/
    litestream replicate /app/db.sqlite3 "${REPLICA_URL}"
    """
    import os
    import subprocess

    db_path = _get_sqlite_db_path()
    os.environ.setdefault("DATABASE_PATH", db_path)

    if len(argv) > 2:
        subprocess.run(["litestream"] + argv[2:])
        exit(0)
    subprocess.run(["litestream", "replicate"])


def run_qcluster(argv: list) -> None:
    """Run Django-q cluster."""
    from django.core.management import execute_from_command_line

    execute_from_command_line(argv[2:])


def run_manage(argv: list) -> None:
    """Run Django's manage command."""
    from django.core.management import execute_from_command_line

    execute_from_command_line(argv[1:])


COMMANDS = {
    "qcluster": run_qcluster,
    "manage": run_manage,
    "setup": run_setup,
    "litestream": run_litestream,
}

if __name__ == "__main__":
    main()
