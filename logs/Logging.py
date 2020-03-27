import logging

# from scripts.relative_path import *
import scripts.relative_path

# create logger
module_logger = logging.getLogger('status_application.auxiliary')


class Auxiliary:
    def __init__(self):
        self.logger = logging.getLogger('status_application.auxiliary.Auxiliary')
        self.logger.info('creating an instance of Auxiliary')


# create logger with 'spam_application'
logger = logging.getLogger('status_application')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(get_path('logs/status.log'))
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
