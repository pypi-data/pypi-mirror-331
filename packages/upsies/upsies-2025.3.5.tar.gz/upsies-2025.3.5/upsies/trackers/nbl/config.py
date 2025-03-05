"""
Concrete :class:`~.TrackerConfigBase` subclass for NBL
"""

import base64

from ... import utils
from .. import base

import logging  # isort:skip
_log = logging.getLogger(__name__)


class NblTrackerConfig(base.TrackerConfigBase):
    defaults = {
        'anonymous': utils.configfiles.config_value(
            value=utils.types.Bool('no'),
            description='Whether your username is displayed on your uploads.',
        ),
        'upload_url': base64.b64decode('aHR0cHM6Ly9uZWJ1bGFuY2UuaW8vdXBsb2FkLnBocA==').decode('ascii'),
        'announce_url': utils.configfiles.config_value(
            value='',
            description=(
                'The complete announce URL with your private passkey.\n'
                'Get it from the website: Shows -> Upload -> Your personal announce URL'
            ),
        ),
        'apikey': utils.configfiles.config_value(
            value='',
            description=(
                'Your personal private API key.\n'
                'Get it from the website: <USERNAME> -> Settings -> API keys'
            ),
        ),
        'exclude': (),
    }

    argument_definitions = {
        'submit': {
            ('--anonymous', '--an'): {
                'help': 'Hide your username for this submission',
                'action': 'store_true',
                # This must be `None` so it doesn't override the "anonymous"
                # value from the config file. See CommandBase.get_options().
                'default': None,
            },
            ('--tvmaze', '--tv'): {
                'help': 'TVmaze ID or URL',
                'type': utils.argtypes.webdb_id('tvmaze'),
            },
        },
    }
