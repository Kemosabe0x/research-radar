"""RSSAgent — sports-science journal RSS monitoring and alerts."""

__version__ = "0.1.0"

from rssagent.monitor import check_journals, main

__all__ = ["check_journals", "main", "__version__"]
