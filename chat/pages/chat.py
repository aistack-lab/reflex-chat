from __future__ import annotations

import reflex as rx

from chat.components import chat
from chat.components.templates import templates
from chat.state import State  # Import the state directly
from chat.template import with_template


@rx.page(route="/chat")
@with_template
def chat_page() -> rx.Component:
    """Chat page showing the chat interface."""
    return rx.vstack(
        rx.vstack(
            rx.center(
                rx.image(src="/logo.png", width="100px", height="auto"),
                width="100%",
            ),
            templates(),
            rx.box(
                rx.foreach(
                    State.chats[State.current_chat],
                    chat.message_exchange,
                ),
                width="100%",
                padding_bottom="80px",
            ),
            width="100%",
            max_width="50em",
            padding_x="4px",
            align_self="center",
            margin_x="auto",
            spacing="4",
        ),
        chat.action_bar(),
        width="100%",
        height="100%",
    )
