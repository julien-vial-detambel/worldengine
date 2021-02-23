import colorlog

def init():
    global logger
    logger = colorlog.getLogger()
    logger.setLevel(colorlog.colorlog.logging.DEBUG)

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter())
    logger.addHandler(handler)
