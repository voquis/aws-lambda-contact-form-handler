"""
App handler startup. Sets log level for subsequent modules
"""

import logging
import os

# Configure log level from environment
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.getLogger().setLevel(LOG_LEVEL)
logging.info('Using log level %s', LOG_LEVEL)
