"""
Tools for creating arg parsers that are preconfigured for
lettersmith scripts.
"""
import argparse
from voluptuous import Schema, Optional, ALLOW_EXTRA
from .yamltools import load


def add_config_argument(parser):
    """
    Append a Lettersmith config argument to an argument parser.
    config should be a path to a YAML config file.
    """
    parser.add_argument(
        'config',
        help="Path to a YAML config file",
        type=load,
        default={}
    )
    return parser


site_schema = Schema({
    Optional("title", default="My Website"): str,
    Optional("description", default=""): str,
    Optional("author", default=""): str
}, extra=ALLOW_EXTRA)

site_schema.__doc__ = """
Schema site property of Lettersmith YAML config files.

May have additional user-defined keys in addition to the ones listed in schema.
"""

schema = Schema({
    Optional("input_path", default="content"): str,
    Optional("output_path", default="public"): str,
    Optional("theme_path", default="theme"): str,
    Optional("data_path", default="data"): str,
    Optional("static_paths", default=[]): [str],
    Optional("base_url", default="/"): str,
    Optional("build_drafts", default=False): bool,
    Optional("site", default={}): site_schema
})
schema.__doc__ = """
Schema for Lettersmith YAML config files.
"""