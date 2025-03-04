from dataclasses import dataclass
import logging


@dataclass
class LoggingConfig:
    """
    Logging configuration dataclass.

    level: The logging level to use.
    filepath: The filepath to write the log to.
    log_entry_format: The format of the log entry.
    date_format: The format of the date in the log entry.
    """
    level: int
    filepath: str
    log_entry_format: str
    date_format: str

    def __post_init__(self):
        level = getattr(logging, self.level.upper())
        logging.basicConfig(
            filename=self.filepath,
            format=self.log_entry_format,
            level=level,
            datefmt=self.date_format,
        )
