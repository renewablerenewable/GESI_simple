import logging


class LoggerCore:
    def __init__(self, logger):
        self._logger = logger
        self._logger.setLevel(logging.INFO)

        self._logger.addFilter(LoggerFilter())

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt='[%(asctime)s @@ %(tag)s] %(message)s', datefmt='%H:%M:%S')
        stream_handler.setFormatter(formatter)

        self._logger.addHandler(stream_handler)

    @staticmethod
    def create_logger(name):
        logger = logging.getLogger(name)
        return LoggerCore(logger)

    def debug(self, tag, msg):
        extra = {'tag': tag}
        self._logger.debug(msg, extra)

    def error(self, tag, msg):
        extra = {'tag': tag}
        self._logger.error(msg, extra)

    def info(self, tag, msg):
        extra = {'tag': tag}
        self._logger.info(msg, extra)

    def warning(self, tag, msg):
        extra = {'tag': tag}
        self._logger.warning(msg, extra)


class LoggerFilter(logging.Filter):
    def filter(self, record):
        record.tag = record.args.get('tag')
        return True
