import logging
import os
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
class CustomFormatter(logging.Formatter):

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        
        level: logging.Formatter(
            (
            "[\x1b[30;1m{asctime}\x1b[0m] "
            f"{colour}"
            "{levelname:<8}\x1b[0m [\x1b[35m{name}\x1b[0m] "
            "[{module}:{funcName}:{lineno}] {message}"
            ),
            '%Y-%m-%d %H:%M:%S', style='{'
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        
        record.exc_text = None
        return output
    


class FileFormatter(Formatter):
    log_format = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s"

    def format(self, record):
        formatter = Formatter(fmt=self.log_format, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)



def create_file_handler(log_dir, logger_name):
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y_%m_%d')}_{logger_name}.log")
    file_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=0, encoding="utf-8")
    file_handler.setFormatter(FileFormatter())
    file_handler.setLevel(logging.DEBUG)  
    return file_handler



def create_console_handler(level=logging.DEBUG):
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    console_handler.setLevel(level)  
    return console_handler


if __name__ == "__main__":
    
    bot_logger = logging.getLogger("bot")
    bot_logger.setLevel(logging.DEBUG)
    bot_logger.addHandler(create_console_handler())  
    bot_logger.addHandler(create_file_handler("./logs", "internal"))  

    
    pull_logger = logging.getLogger("pull")
    pull_logger.setLevel(logging.DEBUG)
    pull_logger.addHandler(create_console_handler(logging.INFO))  
    pull_logger.addHandler(create_file_handler("./logs/cogs/single/pull", "pull"))  

    bot_logger.debug("This is a DEBUG message from bot.")
    bot_logger.info("This is an INFO message from bot.")
    pull_logger.debug("This is a DEBUG message from pull.")
    pull_logger.info("This is an INFO message from pull.")
