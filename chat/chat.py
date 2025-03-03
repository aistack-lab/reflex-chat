"""The main Chat app."""

from __future__ import annotations

import reflex as rx
import reflex_chakra as rc

from chat.components import chat, navbar


def index() -> rx.Component:
    """The main app."""
    return rc.vstack(
        navbar(),
        chat.chat(),
        chat.action_bar(),
        background_color=rx.color("mauve", 1),
        color=rx.color("mauve", 12),
        min_height="100vh",
        align_items="stretch",
        spacing="0",
    )


# Add state and page to the app.
theme = rx.theme(appearance="dark", accent_color="cyan", scaling="110%", radius="small")
app = rx.App(theme=theme)
app.add_page(index)
