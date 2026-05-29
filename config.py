#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(description="Dream Park HTTP server")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--run-webpage", action='store_true', default=False)

args = parser.parse_args()