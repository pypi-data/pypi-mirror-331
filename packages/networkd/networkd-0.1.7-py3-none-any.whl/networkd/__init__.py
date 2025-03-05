# read version from installed package
from importlib.metadata import version
__version__ = version("networkd")

from .networkd import Embed

prep_data = Embed.prep_data
filter_df = Embed.filter_df
co_occurence = Embed.co_occurence
embed = Embed.embed


__all__ = ['prep_data', 'filter_df', 'co_occurence', 'embed']
