import re, sys, time  # noqa E401
from enum import Enum

__all__ = ["Colors", "ColorLogger"]


SUPPORTED_PLATFORMS = ["linux", "win32", "darwin"]


class ANSINotSupportedError(Exception):
    def __init__(self, platform):
        super().__init__(f"ANSI colors are not supported on platform: {platform}")


class Colors(Enum):
    """
    ANSI color codes for styling console output.
    Provides foreground, background colors, and text styles.
    """
    def __str__(self):
        if not any(sys.platform.startswith(platform) for platform in SUPPORTED_PLATFORMS):
            raise ANSINotSupportedError(f"ANSI colors are not supported on platform: {sys.platform}")
        return self.value

    # Foreground colors
    RED = "\033[38;5;124m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    BLACK = "\033[30m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[38;5;214m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

    # Background colors
    RED_BG = "\033[48;5;124m"
    GREEN_BG = "\033[42m"
    BLUE_BG = "\033[44m"
    BLACK_BG = "\033[40m"
    WHITE_BG = "\033[48;5;15m"
    GREY_BG = "\033[48;5;8m"
    LIGHT_RED_BG = "\033[48;5;9m"
    LIGHT_BLUE_BG = "\033[48;5;12m"
    LIGHT_GREEN_BG = "\033[48;5;10m"
    YELLOW_BG = "\033[48;5;11m"
    ORANGE_BG = "\033[48;5;214m"
    CYAN_BG = "\033[46m"
    MAGENTA_BG = "\033[45m"

    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"
    FRAME = "\033[51m"

    RESET = "\033[0m"

    @classmethod
    def available_colors(cls) -> str:
        """Print all available colors and styles with their names."""
        for color in cls:
            print(f"{color.value}{color.name}{Colors.RESET}")
        return ""


class ColorLogger:
    """
    A class for printing colored and formatted messages to the console.

    Example:
    --------
    >>> cprint = ColorLogger()
    >>> # Print text with a red foreground color and bold styling using inline tags
    >>> cprint.log("[red][bold]Hello, World![reset]")  # doctest: +SKIP

    >>> # Print text with a custom purple background and italic styling
    >>> # Use double brackets `[[ ]]` for background colors
    >>> cprint.time("[[#d143b8]]Hello[reset], [cyan][italic]World![reset]")  # doctest: +SKIP

    >>> # Print text exactly as written, including inline tags
    >>> # Use exclamation marks `!` to mark it as ignored styling
    >>> cprint.warning("Color [!#ff0000] and [!blue] styles are ignored")  # doctest: +SKIP
    """

    LEVEL_STYLES = {
        "time": f"\033[30m\033[46m {time.strftime('%H:%M')} \033[0m",  # Black on Cyan
        "error": "\033[30m\033[48;5;9m ERROR \033[0m",  # Black on Red
        "warning": "\033[30m\033[48;5;214m WARNING \033[0m",  # Black on Orange
        "info": "\033[30m\033[46m INFO \033[0m",  # Black on Cyan
        "success": "\033[30m\033[42m SUCCESS \033[0m",  # Black on Green
    }
    PREDEFINED_COLORS = {
        # foreground, background
        "red": ["\033[38;5;124m", "\033[48;5;124m"],
        "green": ["\033[92m", "\033[42m"],
        "blue": ["\033[94m", "\033[44m"],
        "black": ["\033[30m", "\033[40m"],
        "white": ["\033[97m", "\033[48;5;15m"],
        "grey": ["\033[90m", "\033[48;5;8m"],
        "light_red": ["\033[91m", "\033[48;5;9m"],
        "light_blue": ["\033[94m", "\033[48;5;12m"],
        "light_green": ["\033[92m", "\033[48;5;10m"],
        "yellow": ["\033[93m", "\033[48;5;11m"],
        "orange": ["\033[38;5;214m", "\033[48;5;214m"],
        "cyan": ["\033[96m", "\033[46m"],
        "magenta": ["\033[95m", "\033[45m"],

        # Text formatting
        "bold": ["\033[1m", "\033[1m"],
        "italic": ["\033[3m", "\033[3m"],
        "underline": ["\033[4m", "\033[4m"],
        "strikethrough": ["\033[9m", "\033[9m"],
        "frame": ["\033[51m", "\033[51m"],

        # Reset
        "reset": ["\033[0m", "\033[0m"]
    }

    def __init__(self):
        if not any(sys.platform.startswith(p) for p in SUPPORTED_PLATFORMS):
            raise ANSINotSupportedError(f"ANSI codes are not supported on {sys.platform}")

    @classmethod
    def _apply_formatting(cls, text: str) -> str:
        """Applies ANSI formatting to the text based on inline tags."""
        def replacer(match):
            color_key = match.group(1) or match.group(2)

            if color_key in cls.PREDEFINED_COLORS:
                return cls.PREDEFINED_COLORS[color_key][0] if match.group(1) else cls.PREDEFINED_COLORS[color_key][1]

            if color_key.startswith("#"):
                r, g, b = tuple(int(color_key[i:i+2], 16) for i in (1, 3, 5))
                return f"\033[38;2;{r};{g};{b}m" if match.group(1) else f"\033[48;2;{r};{g};{b}m"

            return match.group(0)

        return re.sub(r"\[(!?[a-z_]+|#[0-9a-fA-F]{6})]|\[\[(!?[a-z_]+|#[0-9a-fA-F]{6})]]", replacer, text)

    @classmethod
    def log(cls, text: str):
        """Logs a plain message without any styling or timestamp."""
        print(cls._apply_formatting(text))

    @classmethod
    def time(cls, text: str):
        """Logs a message with a timestamp, indicating the time of the log entry."""
        print(f"{cls.LEVEL_STYLES['time']} {cls._apply_formatting(text)}")

    @classmethod
    def error(cls, text: str):
        """Logs an error message in red with an 'ERROR' prefix."""
        txt = f"[light_red]{text}[reset]"
        print(f"{cls.LEVEL_STYLES['error']} {cls._apply_formatting(txt)}")

    @classmethod
    def warning(cls, text: str):
        """Logs a warning message in orange with a 'WARNING' prefix, signaling potential issues."""
        txt = f"[orange]{text}[reset]"
        print(f"{cls.LEVEL_STYLES['warning']} {cls._apply_formatting(txt)}")

    @classmethod
    def info(cls, text: str):
        """Logs an informational message in cyan with an 'INFO' prefix, used for general updates."""
        txt = f"[cyan]{text}[reset]"
        print(f"{cls.LEVEL_STYLES['info']} {cls._apply_formatting(txt)}")

    @classmethod
    def success(cls, text: str):
        """Logs a success message in green with a 'SUCCESS' prefix, indicating a completed action."""
        txt = f"[green]{text}[reset]"
        print(f"{cls.LEVEL_STYLES['success']} {cls._apply_formatting(txt)}")
