from importlib import metadata as _metadata

from ycf.servers import YcfServer
from ycf.types import AliceSkillRequest, Context, HttpRequest, HttpResponse, MessagesQueueRequest

try:
    __version__ = _metadata.version('ycf-tools')

except _metadata.PackageNotFoundError:
    __version__ = '0.0.0'

__all__ = [
    'YcfServer',
    'AliceSkillRequest',
    'Context',
    'HttpRequest',
    'HttpResponse',
    'MessagesQueueRequest',
]
