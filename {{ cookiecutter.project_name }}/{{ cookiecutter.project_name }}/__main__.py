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
        run_granian(sys.argv)


def run_setup(_):
    """Run some project setup tasks"""
    from django.core.management import execute_from_command_line
    from django.core.management.base import CommandError
    from contextlib import suppress

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


def run_granian(argv: list) -> None:
    """
    Run granian the WSGI server.
    https://github.com/emmett-framework/granian
    """
    import multiprocessing
    import granian
    from granian.constants import Interfaces

    workers = multiprocessing.cpu_count() * 2 + 1
    granian.Granian(
        "{{ cookiecutter.project_name }}.wsgi:application",
        interface=Interfaces.WSGI,
        workers=workers,
        address="127.0.0.1",
        port=8000,
    ).serve()


def run_litestream(argv: list) -> None:
    """Run Litestream via django-litestream."""
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage", "litestream", *argv[2:]])


def run_qcluster(argv: list) -> None:
    """Run Django-q cluster."""
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage", "qcluster", *argv[2:]])


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
