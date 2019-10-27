"""
Command line tool for scaffolding Lettersmith sites.
"""
from pathlib import Path, PurePath
from os import makedirs
import shutil
import argparse
import random


parser = argparse.ArgumentParser(
    description="""A tool for scaffolding Lettersmith sites""")
parser.add_argument("project_path",
    type=Path,
    help="Path to your project directory")
parser.add_argument("-t", "--type",
    type=str, default='blog', choices=["blog"],
    help="The type of project to scaffold")
args = parser.parse_args()


def main():
    project_path = Path(args.project_path)
    module_path = Path(__file__).parent
    scaffold_path = Path(
        module_path, "..", "package_data", "scaffold", args.type)

    shutil.copytree(scaffold_path, project_path)

    messages = (
        "Hocus pocus — Your new site is ready!",
        "Alakazam — Your new site is ready!",
        "Tada — Your new site is ready!",
        "A wild website appears!"
    )

    print(random.choice(messages))
