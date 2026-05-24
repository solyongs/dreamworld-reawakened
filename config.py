#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(description="Dream Park HTTP server")
parser.add_argument("port", nargs="?", type=int, default=8080)
parser.add_argument("--debug", action="store_true")
parser.add_argument("--random", action="store_true", default=False)
parser.add_argument("--run-webpage", action='store_true', default=False)
parser.add_argument("--game_sync", action="store_true", help="Enable Game Sync support")

args = parser.parse_args()