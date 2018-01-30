"""
Tools for creating arg parsers that are preconfigured for
lettersmith scripts.
"""
import argparse
from pathlib import Path
from .yamltools import load

from lettersmith import paging


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


def read_config(config):
    """
    Reads config object, providing sensible defaults for properties
    that aren't defined.
    """
    return {
        "input_path": config.get("input_path", "content"),
        "output_path": config.get("output_path", "public"),
        "cache_path": config.get("cache_path", ".lettersmith_cache"),
        "theme_path": config.get("theme_path", "theme"),
        "data_path": config.get("data_path", "data"),
        "static_paths": config.get("static_paths", []),
        "base_url": config.get("base_url", "/"),
        "build_drafts": config.get("build_drafts", False),
        "permalink_templates": config.get("permalink_templates", {}),
        "taxonomies": config.get("taxonomies", []),
        "paging": paging.read_config(config),
        "site": config.get("site", {})
    }