import logging
import logging.config
import sys

LOGGERS = []

logging.basicConfig(
    format='%(asctime)s : %(levelname)-16s %(name)-32s %(message)-32s',
    filename="journal.log",
    level=logging.DEBUG
)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})


def get_logger(package, component="/"):
    from config_app import LOGGING
    logger = logging.getLogger(package)
    if f'{package}{component}' not in LOGGERS:
        logger.handlers.clear()
        handler = logging.StreamHandler(sys.stdout)
        component = component + \
            ''.join([" " for _ in range(24 - len(component))])
        formatter = logging.Formatter(
            f'%(asctime)s : %(levelname)-12s %(name)-24s  {component} %(message)-24s')
        handler.setFormatter(formatter)
        if LOGGING:
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        LOGGERS.append(f'{package}{component}')
    return logger