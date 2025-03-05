import aiobtclientapi

from . import base
from .. import config, utils


class TransmissionBtClient(base.BtClientBase):
    class Config(base.BtClientConfigBase):
        client: str = 'transmission'
        url: base.ClientUrl(aiobtclientapi.TransmissionAPI)
