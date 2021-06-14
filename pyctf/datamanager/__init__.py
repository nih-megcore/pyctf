"""Data management.

    This module contains DataCache, an easy to use keyed data cache,
    and FilterTrials, which is a class that automatically reads, segments,
    filters, and caches MEG timeseries data.

    @@@

"""

__all__ = ['DataCache', 'FilterTrials']

from .DataCache import DataCache
from .FilterTrials import FilterTrials

__version__ = 1.0

# @@@
# trial vs segment filtering
# add verbose mode output detailing cache usage
# covariance class
