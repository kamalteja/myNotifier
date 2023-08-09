#!/usr/bin/env python3

import os

from freerider.arguments import rider_arguments
from freerider.plugins.hertz import hertz_rides

PLUGINS = [(hertz_rides, rider_arguments)]
CACHE_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/cache.json"


def main():
    """Entry point for myNotifier"""
    for plugin, arguments in PLUGINS:
        print(f"Calling plugin: {plugin.__name__}")
        args = arguments()
        plugin(args)


if __name__ == "__main__":
    main()
