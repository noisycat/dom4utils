#!/usr/bin/env python
b"We currently require Python 2.6 or later"
from __future__ import print_function, division
import sys
import argparse
parser = argparse.ArgumentParser(description='Dominions 4 Map Editor')

import Map, MapData, MapImage, MapGUI

if __name__ == '__main__':
    parser.parse_args()
    print("Starting MapEditor")

