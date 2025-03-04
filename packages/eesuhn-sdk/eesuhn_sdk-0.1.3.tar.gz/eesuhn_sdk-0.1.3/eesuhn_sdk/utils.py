from .ansi import Back


def print_error(
    m: str
) -> None:
    print(f"{Back.RED}ERROR{Back.RESET} {m}")


def print_warning(
    m: str
) -> None:
    print(f"{Back.YELLOW}WARNING{Back.RESET} {m}")


def print_info(
    m: str
) -> None:
    print(f"{Back.MAGENTA}INFO{Back.RESET} {m}")


def print_success(
    m: str
) -> None:
    print(f"{Back.GREEN}SUCCESS{Back.RESET} {m}")
