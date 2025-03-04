import subprocess
import sys
from functools import partial
from typing import Any
from typing import Callable
from typing import List
from typing import NamedTuple


class RerCommand(NamedTuple):
    main_command: str
    others: List[str]

    def as_args(self) -> List[str]:
        return [self.main_command] + self.others


def run_pip(
    args: List[Any], out_to=None, callback: Callable[[], None] | None = None
) -> None:
    try:
        result = subprocess.run(["pip"] + args, stdout=out_to, check=True)
        if not (callback is None):
            callback()
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def update_requirements(requirements_filename: str) -> None:
    with open(requirements_filename, "w") as f:
        run_pip(["list", "--format=freeze"], f)


def main():
    cmd = RerCommand(sys.argv[1], sys.argv[2:])
    requirements_filename = "requirements.txt"
    match cmd.main_command:
        case "freeze":
            run_pip(["list", "--format=freeze"])
        case "add":
            run_pip(
                ["install"] + cmd.others,
                callback=partial(update_requirements, requirements_filename),
            )
        case "install":
            run_pip(
                cmd.as_args(),
                callback=partial(update_requirements, requirements_filename),
            )
        case "uninstall":
            run_pip(
                cmd.as_args(),
                callback=partial(update_requirements, requirements_filename),
            )
        case "init":
            update_requirements("requirements.txt")
        case _:
            run_pip(cmd.as_args())


if __name__ == "__main__":
    main()
