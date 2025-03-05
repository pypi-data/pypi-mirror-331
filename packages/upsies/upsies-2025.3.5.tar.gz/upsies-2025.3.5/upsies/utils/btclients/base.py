import abc
import typing

import aiobtclientapi
import aiobtclientrpc
import pydantic
import pydantic_core


class BtClientBase(abc.ABC):
    """
    Thin wrapper class around a :class:`aiobtclientapi.APIBase` subclass

    :param name: Name of the client (see
        :func:`aiobtclientapi.names`)
    :param url: How to connect to the client API
    :param username: API password for authentication
    :param password: API password for authentication
    :param download_path: Where to download added torrents to
    :param check_after_add: Verify added torrents if content already exists
    :param category: Add torrents to this category if the client supports
        categories
    """

    @abc.abstractmethod
    def Config(self):
        """..."""
        pass

    def __init__(self, name, *, config):
        self._api = aiobtclientapi.api(
            name=config['name'],
            url=config['url'],
            username=config['username'],
            password=config['password'],
        )
        self._config = config

    @property
    def name(self):
        """Name of the client (same as :attr:`aiobtclientrpc.RPCBase.name`)"""
        return self._api.name

    @property
    def label(self):
        """Label of the client (same as :attr:`aiobtclientrpc.RPCBase.label`)"""
        return self._api.label

    async def add_torrent(self, torrent):
        """
        Add `torrent` to client

        :param torrent: ``.torrent`` file/URL, magnet link or infohash
        """
        _log.debug('Adding %s to %s with config=%s', torrent, self.name, self._config)
        response = await self._api.add(
            torrent,
            location=self._config['download_path'],
            # "check_after_add" options is not implemented by all clients.
            verify=self._config.get('check_after_add', False),
        )

        if response.errors:
            for error in response.errors:
                raise errors.TorrentAddError(error)
        else:
            infohash = (response.added + response.already_added)[0]

            if 'category' in self._config:
                await self._set_category(infohash, str(self._config['category']))

            return infohash

    async def _set_category(self, infohash, category):
        if self._api.name != 'qbittorrent':
            raise RuntimeError(f'Categories are not supported for {self._api.label}')
        else:
            try:
                await self._api.call(
                    'torrents/setCategory',
                    hashes=infohash,
                    category=str(category),
                )
            except aiobtclientrpc.RPCError as e:
                if 'incorrect category name' in str(e).lower():
                    raise errors.TorrentAddError(f'Unknown category: {category}') from e
                else:
                    raise e


class BtClientConfigBase(utils.config.SubsectionBase):
    """
    ...
    """

    client: typing.Literal[*client_names()] = pydantic.Field(
        description='Client name (' + ', '.join(name for name in client_names()) + ')',
    )

    username: str = pydantic.Field(
        default='',
        description='Username for authentication',
    )

    password: pydantic.SecretStr = pydantic.Field(
        default='',
        description='Password for authentication',
    )

    translate_path: typing.Annotated[
        utils.types.PathTranslations,
        pydantic.Field(
            default=(),
            description=(
                f'Translate absolute paths on the computer that is running {__project_name__} (LOCAL) '
                'to paths on the computer that is running {client.label} (REMOTE)\n'
                'This is a list where LOCAL and REMOTE are separated by "->". Spaces are trimmed. '
                'When adding a torrent, LOCAL in the content path is replaced with REMOTE to get '
                "the path where the BitTorrent client can find the torrent's files.\n"
                'Example:\n'
                'clients.{client.name}.translate_path =\n'
                '  /home/me/My Projects -> /storage/seed_forever\n'
                '  /media/me/USB/ -> /storage/seed_temporarily\n'
            ),
        ),
        pydantic.BeforeValidator(utils.types.PathTranslations),
    ]

    def __new__(cls, *args, **kwargs):
        # Derive our subclass from the required "client" field.
        if 'client' in kwargs:
            # Get "client" from provided keyword arguments.
            client = kwargs['client']
        elif (
                'client' in cls.model_fields
                and cls.model_fields['client'].default is not pydantic_core.PydanticUndefined
        ):
            # Get "client" from default value provided by the subclass.
            client = cls.model_fields['client'].default
        else:
            raise ValueError('Required client field is missing')

        try:
            # subcls = {
            #     'deluge': DelugeBtClient.Config,
            #     'transmission': TransmissionBtClient.Config,
            # }[client.lower()]
            subcls = utils.btclients.get_client_class(client)

        except KeyError:
            raise errors.ConfigError(f'Invalid client: {client}')

        # print('INSTANTIATING', repr(subcls), 'WITH', args, kwargs)
        return super().__new__(subcls)


CheckAfterAdd = typing.Annotated[
    utils.types.Bool,
    pydantic.Field(
        default='no',
        description='Whether added torrents should be hash checked',
    ),
    pydantic.BeforeValidator(utils.types.Bool),
]
"""..."""


def ClientUrl(API):
    """
    Return :class:`~.typing.Annotated` `API`

    :param API: :class:`aiobtclientapi.APIBase` subclass
    """
    return typing.Annotated[
        API.URL,
        pydantic.Field(
            default=API.URL.default,
            description=f'URL of the {API.label} RPC interface',
        ),
        pydantic.BeforeValidator(API.URL),
    ]
