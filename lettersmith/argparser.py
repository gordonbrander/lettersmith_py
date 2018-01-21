"""
Tools for creating arg parsers that are preconfigured for
lettersmith scripts.
"""
import argparse
from pathlib import Path
from .yamltools import load


def lettersmith_argparser(description="Builds a site with Lettersmith"):
    """
    Creates a Lettersmith argparser. You supply the description. This
    makes it easy to create your own static site generator, and have a
    useful description text for it.
    """
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