import logging


class QFLogger():

    def __init__(self, logger_name='default_logger_name',
                 log_file='app.log',
                 log_level=logging.INFO):

        # Create a custom logger
        self.logger = logging.getLogger(self.get_logger_name(logger_name))

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s : %(message)s')
        f_format = logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s : %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

        self.logger.setLevel(log_level)

    def get_logger(self):
        return self.logger

    def get_logger_name(self, logger_name):
        name = logger_name.split('.')
        return name[len(name)-1]
