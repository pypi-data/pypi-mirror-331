"""Types used in HTMLReport class."""

from __future__ import annotations

from typing import Literal

CallbackType = Literal[
    "application",
    "infrastructure",
    "service",
    "interaction",
    "node",
    "link",
    "simulation",
]

PlotType = Literal["bar", "line", "scatter"]
