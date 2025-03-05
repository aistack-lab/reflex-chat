"""Template layout for consistent page structure."""

from __future__ import annotations

from typing import TYPE_CHECKING

import reflex as rx
import reflex_chakra as rc

from chat.components import navbar
from chat.components.menu import menus_v1


if TYPE_CHECKING:
    from collections.abc import Callable


def template(page_content: rx.Component) -> rx.Component:
    """Apply consistent layout to pages.

    Args:
        page_content: The main content component to display

    Returns:
        A component with consistent layout
    """
    sidebar_width = 275

    return rc.vstack(
        navbar(),
        rx.hstack(
            # Left sidebar menu
            rx.box(
                rx.box(
                    menus_v1(),
                    transform="scale(1.25)",
                    transform_origin="top left",
                    width="80%",
                    height="auto",
                    padding="0.5em",
                ),
                position="fixed",
                left="0",
                top="60px",
                bottom="60px",
                padding="1em",
                width=f"{sidebar_width}px",
                border_right=f"1px solid {rx.color('mauve', 3)}",
                background_color=rx.color("mauve", 2),
                overflow="hidden",
                z_index="10",
            ),
            # Main content area with scrolling
            rx.box(
                page_content,
                width=f"calc(100% - {sidebar_width}px)",
                height="calc(100vh - 60px)",  # Subtract navbar height
                margin_left=f"{sidebar_width}px",
                overflow_y="auto",  # Enable vertical scrolling
                padding_y="8",
            ),
            spacing="0",
            width="100%",
            height="calc(100vh - 60px)",  # Adjusted for navbar height
        ),
        background_color=rx.color("mauve", 1),
        color=rx.color("mauve", 12),
        min_height="100vh",
        align_items="stretch",
        spacing="0",
        width="100%",
        position="relative",
    )


def with_template(
    page_function: Callable[[], rx.Component],
) -> Callable[[], rx.Component]:
    """Decorator to wrap a page function with the template.

    Args:
        page_function: Function that returns page content

    Returns:
        Function that returns templated page
    """

    def wrapped_page() -> rx.Component:
        return template(page_function())

    # Copy any metadata from the original function
    wrapped_page.__name__ = page_function.__name__
    wrapped_page.__doc__ = page_function.__doc__

    # This is no longer needed as Reflex handles route through the @rx.page decorator
    # But let's preserve any other attributes just in case
    for attr, value in page_function.__dict__.items():
        setattr(wrapped_page, attr, value)

    return wrapped_page
