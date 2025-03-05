import logging

from shared_libraries.core.logger.formatter import CustomFormatter, LogColors, Colors


class CustomLogger:
    def __init__(self, name: str, log_level: str):
        self.logger = logging.getLogger(name)
        if not self.logger.hasHandlers():
            level = getattr(logging, log_level.upper(), None)
            if not isinstance(level, int):
                raise ValueError(f"Invalid log level: {log_level}")
            self.logger.setLevel(level)
            handler = logging.StreamHandler()
            handler.setFormatter(CustomFormatter())
            self.logger.addHandler(handler)

    def _log(self, level: int, msg: str, color: LogColors = None, *args, **kwargs):
        if color:
            original_formatter = self.logger.handlers[0].formatter
            color_fmt = f"{Colors.get_color(color)}{CustomFormatter.base_format}{Colors.RESET}"
            formatter = logging.Formatter(fmt=color_fmt)
            self.logger.handlers[0].setFormatter(formatter)

        self.logger.log(level, msg, *args, **kwargs)

        if color:
            self.logger.handlers[0].setFormatter(original_formatter)

    def debug(self, msg, color: LogColors = None, *args, **kwargs):
        self._log(logging.DEBUG, msg, color, *args, **kwargs)

    def info(self, msg, color: LogColors = None, *args, **kwargs):
        self._log(logging.INFO, msg, color, *args, **kwargs)

    def warning(self, msg, color: LogColors = None, *args, **kwargs):
        self._log(logging.WARNING, msg, color, *args, **kwargs)

    def error(self, msg, color: LogColors = None, *args, **kwargs):
        self._log(logging.ERROR, msg, color, *args, **kwargs)

    def critical(self, msg, color: LogColors = None, *args, **kwargs):
        self._log(logging.CRITICAL, msg, color, *args, **kwargs)


def create_logger(log_level: str = "info") -> CustomLogger:
    return CustomLogger(name='Babylon', log_level=log_level)


logger = create_logger(log_level="info")
