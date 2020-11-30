from pathlib import Path

from jinja2 import Environment, FileSystemLoader


# Engine setup.
def load_j2_template_engine(template_file_path: str):
    """ Loads a J2 template engine from given template file path. """
    # Template file
    template_file = Path(template_file_path)

    # Template directory.
    resolved_template_dir_path = template_file.parent.resolve(strict=True)

    # Load J2 environment.
    j2_environment = Environment(
        loader=FileSystemLoader(str(resolved_template_dir_path))
    )

    # Return template.
    return j2_environment.get_template(template_file.name)
