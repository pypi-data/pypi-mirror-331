"""The Flexdown CLI.""" ""

from pathlib import Path

import typer
from reflex.utils.processes import new_process

from flexdown import constants

# The command line app.
app = typer.Typer()


@app.command()
def run(path: Path):
    """Run a Flexdown project."""
    # Create a .flexdown directory in the current directory.
    constants.FLEXDOWN_DIR.mkdir(parents=True, exist_ok=True)

    # Create a reflex project.
    new_process(
        ["reflex", "init", "--template", "blank"],
        cwd=constants.FLEXDOWN_DIR,
        show_logs=True,
        run=True,
    )

    # Replace the app file with a template.
    constants.FLEXDOWN_FILE.write_text(
        constants.APP_TEMPLATE.format(
            path=Path().absolute() / path,
            module_name=path.stem,
        )
    )

    # Run the reflex project.
    new_process(
        ["reflex", "run"],
        cwd=constants.FLEXDOWN_DIR,
        show_logs=True,
        run=True,
    )
