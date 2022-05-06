import logging
from logging.handlers import RotatingFileHandler

def get_logger(log_file):
    
    # legacy
    # logging.basicConfig(
    #     filename='backup_droplet1.log',
    #     level=logging.DEBUG,
    #     datefmt="%m-%d-%Y %H:%M:%S",
    #     format='%(asctime)s %(levelname)-8s %(message)s',
    # )

    # setup logger
    log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler = RotatingFileHandler(
        log_file,
        mode='a',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=2,
        encoding=None,
        delay=0,
    )
    handler.setFormatter(log_formatter)
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger