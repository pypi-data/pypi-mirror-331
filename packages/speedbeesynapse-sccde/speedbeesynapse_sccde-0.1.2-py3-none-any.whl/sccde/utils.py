"""SpeeDBeeSynapse custom component development environment tool."""
import sys


def print_info(*args: any) -> None:
    """Output information message to standard output."""
    print(*args)  # noqa: T201


def print_error(*args: any) -> None:
    """Output error message to standard error."""
    print(*args, file=sys.stderr)  # noqa: T201
