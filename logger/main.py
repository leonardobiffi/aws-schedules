import logging, os

# Create Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Debug if enable
debugmode = os.getenv('DEBUG', False)
if debugmode:
    # Format Log
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)