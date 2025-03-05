"""ExecBlock class definition."""

import sys
from pathlib import Path

import reflex as rx

from flexdown import types
from flexdown.blocks.block import Block


class ExecBlock(Block):
    """A block of executable Python code."""

    starting_indicator = "```python exec"
    ending_indicator = "```"

    def render(self, env: types.Env) -> rx.Component:
        # Get the content of the block.
        content = self.get_content(env)

        # Get the directory of the filename.
        if self.filename is not None:
            directory = Path(self.filename).resolve().parent

            # Add the directory to the Python path.
            sys.path.insert(0, str(directory))

        env["__xd"].exec(content, env, self.filename)

        # Clean up the Python path.
        if self.filename is not None:
            sys.path.remove(str(directory))

        # Return an empty fragment.
        return rx.fragment()
