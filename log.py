"""
a logger module that would produce logs at varying levels.

Usage:

# init
import log
l=log.getLogger(__name__)

# usage
l.debug("Module starting")
l.error("Error occured!")
l.info("Statistics: %02f",stat_val)

"""

import os
import re
import sys
from logging import getLogger
from logging.config import fileConfig
from io import StringIO
from typing import TextIO

# and our own config file section
LOG_CONFIG_TEMPLATE_FILE = "log.ini"
log_file_path_re = re.compile(r"LOG_FILE_PATH")
EMERGENCY_LOGGER: StringIO = StringIO(
    """
[loggers]
keys: root,log

[handlers]
keys: stderr

[formatters]
keys: std

[logger_root]
level: ERROR
handlers: stderr

[logger_log]
level: INFO
handlers: stderr
propagate: 1
qualname: log

[handler_stderr]
class: StreamHandler
formatter: std
level: NOTSET
args: (sys.stderr, )

[formatter_std]
format: %(asctime)s %(name)s %(levelname)s [%(threadName)s] %(module)s:%(lineno)d %(message)s
datefmt: %Y-%b-%d %H:%M:%S
"""
)

LOG_FILE_NAME = "podsync-cleaner.log"

# Initialise the logging subsystem
# locate the configuration file in the folder we run from
my_path: str = os.path.split(sys.argv[0])[0]
conf_template_file: str = os.path.join(my_path, LOG_CONFIG_TEMPLATE_FILE)
log_file_path: str = os.path.join(my_path, LOG_FILE_NAME)
emergency_logging: bool = False

if os.path.exists(conf_template_file) and log_file_path is not None:
    # modify the configuration file in memory
    # add the configured target file to the file
    new_config: StringIO = StringIO()
    template_file: TextIO = open(conf_template_file, "rt")
    log_file_abspath: str = os.path.abspath(log_file_path)
    for line in template_file:
        new_config.write(log_file_path_re.sub(repr(log_file_abspath), line))
    # rewind the memory file in preparation for using it as a
    # configuration file
    new_config.seek(0)
    fileConfig(new_config)
else:
    # couldn't find the file,but we can still work
    emergency_logging = True
    fileConfig(EMERGENCY_LOGGER)

# we deserve our own logger!
l = getLogger("log")
if emergency_logging:
    l.warning("Logging configuration file not found. " "Logging to STDOUT only")
l.info("Logging subsystem initialised")
