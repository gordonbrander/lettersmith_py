import yaml
import frontmatter


ParserError = yaml.parser.ParserError
ScannerError = yaml.scanner.ScannerError


def load_frontmatter(pathlike):
    with open(str(pathlike)) as f:
        try:
            meta, content = frontmatter.parse(f.read())
            return meta, content
        # Raise a more descriptive errors
        except ParserError as error:
            raise ParserError(
                'Could not parse YAML from frontmatter in "{}"'.format(pathlike)
            ) from error
        except ScannerError as error:
            raise ScannerError(
                'Error scanning "{}"'.format(pathlike)
            ) from error


def load(file_path):
    """
    Given a file path, read the file contents and parse YAML to
    python dict. Returns a python dict.
    """
    with open(file_path, "r") as f:
        return yaml.load(f.read())
    return {}


loads = yaml.load