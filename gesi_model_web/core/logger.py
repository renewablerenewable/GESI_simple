

class Logger:
    def __init__(self, tag, logger):
        self._tag = tag
        self._logger = logger

    def get_logger(self):
        return self._logger

    def print_debug_line(self, msg):
        self._logger.debug(self._tag, msg)

    def print_error_line(self, msg):
        self._logger.error(self._tag, msg)

    def print_info_line(self, msg):
        self._logger.info(self._tag, msg)

    def print_waring_line(self, msg):
        self._logger.warning(self._tag, msg)
