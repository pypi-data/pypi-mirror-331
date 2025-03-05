import pydantic

from .. import utils


class ImageHostConfigBase(utils.config.SubsectionBase):
    """
    Image host configuration
    """

    # Informal client name used in config file. Must be set by subclass.
    thumb_width: int = pydantic.Field(
        default=0,
        description=(
            'Thumbnail width in pixels or 0 for no thumbnail. '
            'Trackers may ignore this option and use a hardcoded thumbnail width.'
        ),
    )


class DummyImageHostConfig(ImageHostConfigBase):
    hostname: str = pydantic.Field(
        default='localhost',
        description='Host name in dummy image URLs.',
    )


class FreeimageImageHostConfig(ImageHostConfigBase):
    base_url: str = pydantic.Field(
        default='https://freeimage.host',
        description=f'Base URL of the API.',
    )
    apikey: pydantic.SecretStr = pydantic.Field(
        default='6d207e02198a847aa98d0a2a901485a5',
        description=(
            'API access key. '
            'The default value is the public API key from https://freeimage.host/page/api.'
        ),
    )


class ImgbbImageHostConfig(ImageHostConfigBase):
    base_url: str = pydantic.Field(
        default='https://api.imgbb.com',
        description=f'Base URL of the API.',
    )
    apikey: pydantic.SecretStr = pydantic.Field(
        default='',
        description=(
            'API access key. '
            'Run ``{__project_name__} ui imgbb -h`` '
            'for instructions on how to get an API key.'
        ),
    )


class ImgboxImageHostConfig(ImageHostConfigBase):
    pass


class PtpimgImageHostConfig(ImageHostConfigBase):
    base_url: str = pydantic.Field(
        default='https://ptpimg.me',
        description=f'Base URL of the API.',
    )
    apikey: pydantic.SecretStr = pydantic.Field(
        default='',
        description=(
            'API access key. '
            'Run ``{__project_name__} ui ptpimg -h`` '
            'for instructions on how to get an API key.'
        ),
    )

def _imagehost_configs():
    imagehost_config_classes = {
        cls.__name__: cls
        for cls in ImageHostConfigBase.__subclasses__()
    }
    imagehost_classes = sorted(
        (imagehost_class for imagehost_class in imagehosts.imghosts()),
        key=lambda imagehost_class: imagehost_class.name,
    )
    imagehost_configs = {}
    for imagehost_class in imagehost_classes:
        imagehost_config_class_name = imagehost_class.__name__ + 'Config'
        imagehost_config_class = imagehost_config_classes[imagehost_config_class_name]
        imagehost_configs[imagehost_class.name] = (imagehost_config_class, imagehost_config_class())
    return imagehost_configs


ImageHostsConfig = pydantic.create_model(
    'ImageHostsConfig',
    **_imagehost_configs(),
    __base__=utils.config.SectionBase,
)
