import os

from zix.server import database, utils
from .common import *


USE_SUBSCRIPTIONS = utils.is_plugin_active("subscriptions")


if utils.is_local():
    from .local import *
else:
    from .server import *
