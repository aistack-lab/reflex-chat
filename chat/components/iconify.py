"""Component for rendering icons using pyconify."""

from __future__ import annotations

from typing import Any, Literal

from pyconify import svg
import reflex as rx


# Define types for better type hinting
Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]
Flip = Literal["horizontal", "vertical", "horizontal,vertical"]


def iconify(
    tag: str,
    color: str | None = None,
    size: int | str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
    **kwargs: Any,
) -> rx.Component:
    """Create an icon using pyconify.

    Args:
        tag: The icon identifier (e.g., "mdi:bell")
        color: Icon color
        size: Shorthand for setting both width and height
        height: Icon height
        width: Icon width
        flip: Flip the icon ("horizontal", "vertical", or "horizontal,vertical")
        rotate: Rotate the icon (90, 180, 270, etc.)
        box: Whether to include viewBox in the SVG
        **kwargs: Additional attributes to pass to rx.html

    Returns:
        A Reflex component containing the icon
    """
    # Set width and height from size if provided
    if size is not None:
        size_value = f"{size}px" if isinstance(size, int) else size
        width = width or size_value
        height = height or size_value

    # Get the SVG as bytes
    svg_bytes = svg(
        tag,
        color=color,
        height=height,
        width=width,
        flip=flip,
        rotate=rotate,
        box=box,
    )

    # Convert bytes to string and use rx.html to render raw HTML
    svg_str = svg_bytes.decode("utf-8")

    return rx.html(svg_str, **kwargs)


if __name__ == "__main__":
    # Example usage
    print(iconify("mdi:bell", color="blue", size=24))
    print(iconify("mdi:account", color="red", rotate=90, flip="horizontal"))
