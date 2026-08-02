"""Renderer registry shared by generation, CLI use, and QA."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .render_overview_svg import render_attention_cycle_overview
from .render_svg import render_svg


Renderer = Callable[[dict[str, Any]], str]

RENDERERS: dict[str, Renderer] = {
    "attention-cycle-overview": render_attention_cycle_overview,
    "reconstruction-timeline": render_svg,
}


def render_view(spec: dict[str, Any], view: dict[str, Any]) -> str:
    """Render one declared view, rejecting unregistered renderer names."""
    try:
        renderer = RENDERERS[view["renderer"]]
    except KeyError as error:
        raise ValueError(
            f'unknown renderer {view["renderer"]} for view {view["id"]}'
        ) from error
    return renderer(spec)
