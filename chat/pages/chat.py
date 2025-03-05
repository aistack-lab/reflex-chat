"""Chat page module."""

from __future__ import annotations

import reflex as rx
import reflex_chakra as rc

from chat.components import chat, navbar


@rx.page(route="/chat")
def chat_page() -> rx.Component:
    """Chat page showing the chat interface."""
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
