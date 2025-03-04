import re


def filter(*args, feed=None, item=None, **kwargs):
    '''The matchtitleregex filter selects only the feed items whose title match the
    given regular expression pattern.

    Example::

      [NASA breaking news]
      url = https://www.nasa.gov/rss/dyn/breaking_news.rss
      filter = feed2exec.plugins.matchtitleregex
      filter_args = ^spam

    The above configuration processes the feed items based on the global
    configuration, but it will skip any item whose title does not start with
    the word "spam".
    '''
    item['skip'] = re.search(' '.join(args), item.get('title', '')) is None
