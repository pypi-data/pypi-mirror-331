import aiobtclientapi

from . import base
from .. import config, utils


class DelugeBtClient(base.BtClientBase):
    class Config(base.BtClientConfigBase):
        client: str = 'deluge'
        url: base.ClientUrl(aiobtclientapi.DelugeAPI)
        check_after_add: base.CheckAfterAdd
