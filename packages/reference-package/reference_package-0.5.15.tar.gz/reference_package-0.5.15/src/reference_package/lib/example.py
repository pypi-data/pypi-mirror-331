"""This is an example module."""

import time

from typeguard import typechecked

from reference_package.lib.constants import DocStrings


@typechecked
def wait_a_second(secs: int = 1, extra_string: str = "") -> None:  # noqa: D103
    print(f"Waiting {secs} seconds.{' ' + extra_string if extra_string else ''}")
    time.sleep(secs)


wait_a_second.__doc__ = DocStrings.EXAMPLE_INTERNAL.api_docstring
