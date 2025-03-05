from ... import utils


def client_names():
    """Return sequence of valid `client_name` names"""
    return tuple(
        cls.Config.client
        for cls in clients()
    )


def clients():
    """Return sequence of :class:`~.BtClientBase` subclasses"""
    return utils.subclasses(BtClientBase, submodules(__package__))


def client_class(client_name):
    """Return :class:`~.BtClientBase` subclass based on :attr:`.BtClientConfigBase.client`"""
    for cls in clients():
        if cls.Config.client == client_name:
            return cls
    raise ValueError(f'Invalid client name: {client_name}')


from .deluge import DelugeBtClient
from .transmission import TransmissionBtClient

print(client_names())

