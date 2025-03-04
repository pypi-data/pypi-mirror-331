import re


def filter(*args, feed=None, item=None, **kwargs):
    '''the droptitleregex filter will drop any feed item with a title matching
    the given regular expression pattern.

    Example::

      [NASA breaking news]
      url = https://www.nasa.gov/rss/dyn/breaking_news.rss
      filter = feed2exec.plugins.droptitleregex
      filter_args = ^ham

    The above configuration processes the feed items based on the global
    configuration, but it will skip any item whose title starts with the word
    "ham".
    '''
    item['skip'] = re.search(' '.join(args), item.get('title', '')) is not None
