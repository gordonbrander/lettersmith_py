"""
Tools for creating arg parsers that are preconfigured for
lettersmith scripts.
"""
import argparse
from pathlib import Path
from .yamltools import load


# A basic parser
def lettersmith_argparser(description="Builds a site with Lettersmith"):
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        'config',
        help="Path to a YAML config file",
        type=load,
        default={}
    )
    return parser