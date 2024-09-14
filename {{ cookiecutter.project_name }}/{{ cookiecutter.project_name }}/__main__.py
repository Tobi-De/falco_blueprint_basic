def main() -> None:
    from pathlib import Path
    import os
    import sys

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


def run_setup(_):
    """Run some project setup tasks"""
    from django.core.management import execute_from_command_line
    from django.core.management.base import CommandError
    from contextlib import suppress

    execute_from_command_line(["manage", "migrate"])
    execute_from_command_line(["manage", "setup_periodic_tasks"])

    with suppress(CommandError):
        execute_from_command_line(
            ["manage", "createsuperuser", "--noinput", "--traceback"]
        )


def run_gunicorn(argv: list) -> None:
    import sys
    import subprocess
    from pathlib import Path

    bin_dir = Path(sys.executable).parent

    argv = argv[1:]
    argv.extend(
        [
            "-c",
            "{{ cookiecutter.project_name }}/gunicorn.py",
            "{{ cookiecutter.project_name }}.wsgi",
        ]
    )
    subprocess.run([bin_dir / "gunicorn", *argv], check=False)


def run_qcluster(argv: list) -> None:
    """Run Django-q cluster."""
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage", "qcluster", *argv[2:]])


def run_manage(argv: list) -> None:
    """Run Django's manage command."""
    from django.core.management import execute_from_command_line

    execute_from_command_line(argv[1:])


COMMANDS = {"qcluster": run_qcluster, "manage": run_manage, "setup": run_setup}


if __name__ == "__main__":
    main()
