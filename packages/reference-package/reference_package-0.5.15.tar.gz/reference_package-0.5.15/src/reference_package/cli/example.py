# noqa: D100
__doc__ = """
.. click:: reference_package.cli.example:main
    :prog: example
    :nested: full
"""

import click
from typeguard import typechecked

from reference_package.lib import example
from reference_package.lib.constants import DocStrings


@click.command(help=DocStrings.EXAMPLE.cli_docstring)
@click.option(
    "--secs", type=int, required=False, default=1, help=DocStrings.EXAMPLE.args["secs"]
)
@typechecked
def main(secs: int = 1) -> None:  # noqa: D103
    example.wait_a_second(secs=secs)
