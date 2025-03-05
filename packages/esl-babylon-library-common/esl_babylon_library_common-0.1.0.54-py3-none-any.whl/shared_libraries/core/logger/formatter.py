import enum
import logging


class LogColors(enum.Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    LIGHT_GRAY = 37
    DARK_GRAY = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    WHITE = 97


class Colors:
    DEBUG = f'\033[{LogColors.CYAN.value}m'  # Cyan
    INFO = f'\033[{LogColors.GREEN.value}m'  # Green
    WARNING = f'\033[{LogColors.BRIGHT_YELLOW.value}m'  # Bright Yellow
    ERROR = f'\033[{LogColors.RED.value}m'  # Red
    CRITICAL = '\033[41m'  # Red background and white text
    RESET = '\033[0m'  # Reset color to default

    @staticmethod
    def get_color(color: LogColors) -> str:
        return f'\033[{color.value}m'


class CustomFormatter(logging.Formatter):
    base_format = "%(asctime)s - %(levelname)s - %(message)s"
    detailed_format = " - Details: (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: f"{Colors.DEBUG}{base_format}{Colors.RESET}",
        logging.INFO: f"{Colors.INFO}{base_format}{Colors.RESET}",
        logging.WARNING: f"{Colors.WARNING}{base_format}{Colors.RESET}",
        logging.ERROR: f"{Colors.ERROR}{base_format}{detailed_format}{Colors.RESET}",
        logging.CRITICAL: f"{Colors.CRITICAL}{base_format}{detailed_format}{Colors.RESET}"
    }

    def format(self,
               record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt)
        return formatter.format(record=record)
