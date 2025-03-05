"""Constants used in flexdown."""

from pathlib import Path

# The extension for Flexdown files.
FLEXDOWN_EXTENSION = ".md"

# The Flexdown app directory.
FLEXDOWN_DIR = Path(".flexdown/flexd")
FLEXDOWN_FILE = FLEXDOWN_DIR / "flexd/flexd.py"
FLEXDOWN_MODULES_DIR = "modules"

# Regex for front matter.
FRONT_MATTER_REGEX = r"^---\s*\n(.+?)\n---\s*\n(.*)$"
# Regex for template placeholders.
TEMPLATE_REGEX_WITHOUT_ESCAPE = r"(?<!\\)(?<!\\\\){(?!\\)(.*?)(?<!\\)}"
TEMPLATE_REGEX = r"{([^{}]*)}"

# The default app template.
APP_TEMPLATE = """import flexdown
import reflex as rx
component_map = {{
    "a": lambda value, **props: rx.link(value, color="blue", **props),
}}
path = "{path}"
{module_name} = flexdown.namespace.FxNamespace(path, prefix=path)
app = flexdown.app(path, component_map=component_map)
"""
