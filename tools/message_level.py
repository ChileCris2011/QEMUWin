import logging

MSG_LEVEL_NUM = 60
logging.addLevelName(MSG_LEVEL_NUM, "MSG")

def msg(message, *args, **kws):
    logger = logging.getLogger()
    if logger.isEnabledFor(MSG_LEVEL_NUM):
        logger._log(MSG_LEVEL_NUM, message, args, **kws)

logging.msg = msg
