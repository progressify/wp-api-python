"""
Test case module.
"""

from time import time
import sys
import logging
import pdb
import functools
import traceback
import copy

CURRENT_TIMESTAMP = int(time())
SHITTY_NONCE = ""
DEFAULT_ENCODING = sys.getdefaultencoding()


def debug_on(*exceptions):
    if not exceptions:
        exceptions = (AssertionError, )

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            prev_root = copy(logging.root)
            try:
                logging.basicConfig(level=logging.DEBUG)
                return f(*args, **kwargs)
            except exceptions:
                info = sys.exc_info()
                traceback.print_exception(*info)
                pdb.post_mortem(info[2])
            finally:
                logging.root = prev_root
        return wrapper
    return decorator
