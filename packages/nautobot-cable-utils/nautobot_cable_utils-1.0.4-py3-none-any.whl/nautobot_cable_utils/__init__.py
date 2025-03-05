from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class CableUtilsConfig(NautobotAppConfig):
    name = "nautobot_cable_utils"
    verbose_name = "Cable Utilities"
    description = "A cable utilities plugin"
    version = __version__
    author = "Gesellschaft für wissenschaftliche Datenverarbeitung mbH Göttingen"
    author_email = "netzadmin@gwdg.de"
    base_url = "nautobot-cable-utils"
    min_version = "2.0.0"
    max_version = "2.9999"


config = CableUtilsConfig
