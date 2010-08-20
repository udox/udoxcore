import logging, sys

"""
See comments in http://www.djangosnippets.org/snippets/1731/

import this module in settings.py to log stuff to apache error log
"""

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)-8s %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)