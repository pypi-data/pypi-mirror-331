import pydantic

from .. import trackers, utils


def _tracker_configs():
    tracker_classes = sorted(
        (tracker_class for tracker_class in trackers.trackers()),
        key=lambda tracker_class: tracker_class.name,
    )
    return {
        tracker_class.name: (tracker_class.TrackerConfig, tracker_class.TrackerConfig())
        for tracker_class in tracker_classes
    }


TrackersConfig = pydantic.create_model(
    'ImghostsConfig',
    **_tracker_configs(),
    __base__=utils.config.SectionBase,
)
