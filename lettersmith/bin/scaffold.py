"""
Command line tool for scaffolding Lettersmith sites.
"""
from pathlib import Path, PurePath
from os import makedirs
import argparse

from lettersmith import yamltools
from lettersmith.file import copy


def main():
    cwd = Path.cwd()
    parser = argparse.ArgumentParser(
        description="""A tool for scaffolding Lettersmith sites""")
    parser.add_argument("project-path",
        type=Path,
        help="Path to your project directory")
    parser.add_argument("-t", "--type",
        type=str, default='wiki', choices=["wiki"],
        help="The type of project to scaffold")
    args = parser.parse_args()

    project_path = Path(args.project_path)
    module_path = Path(__file__).parent
    scaffold_path = Path(
        module_path, "..", "package_data", "scaffold", args.type)

    copy(scaffold_path, project_path, contents=True)

    print("Woo! All done!")