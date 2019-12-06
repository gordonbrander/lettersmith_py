"""
Tools for working with collections of files
"""
from lettersmith.path import glob_files
from lettersmith import file as File
from lettersmith import query


load = query.maps(File.load)


def find(glob):
    """
    Load all docs under input path that match a glob pattern.

    Example:

        docs.find("posts/*.md")
    """
    return load(glob_files(".", glob))


to_doc = query.maps(File.to_doc)
from_doc = query.maps(File.from_doc)