"""Chat components."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import reflex as rx
import reflex_chakra as rc

from chat.components import loading_icon, menu
from chat.state import QA, State


if TYPE_CHECKING:
    from llmling_agent import ChatMessage


message_style: dict[str, Any] = dict(
    display="inline-block",
    padding="1em",
    border_radius="8px",
    max_width=["30em", "30em", "50em", "50em", "50em", "50em"],
)

INPUT_MSG = "Enter a question to get a response."


def input_form() -> rx.Component:
    """A form for entering a question."""
    return rc.form_control(
        rx.hstack(
            rx.input(
                rx.input.slot(rx.tooltip(rx.icon("info", size=18), content=INPUT_MSG)),
                placeholder="Stelle eine Frage...",
                id="question",
                width=["15em", "20em", "45em", "50em", "50em", "50em"],
            ),
            rx.button(
                rx.cond(
                    State.processing,
                    loading_icon(height="1em"),
                    rx.text("Send"),
                ),
                type="submit",
            ),
            align_items="center",
        ),
        is_disabled=State.processing,
    )


def message(message: ChatMessage):
    rx.box(
        rx.badge(
            message.role,
            rx.tooltip(rx.icon("info", size=14), content="The current selected chat."),
            variant="soft",
        ),
        rx.markdown(
            message.content,
            background_color=rx.color("mauve", 4),
            color=rx.color("mauve", 12),
            **message_style,
        ),
        text_align="right",
        margin_top="1em",
    )


def message_exchange(qa: QA) -> rx.Component:
    """A single question/answer message.

    Args:
        qa: The question/answer pair.

    Returns:
        A component displaying the question/answer pair.
    """
    return rx.box(
        rx.box(
            rx.markdown(
                qa.question,
                background_color=rx.color("mauve", 4),
                color=rx.color("mauve", 12),
                **message_style,
            ),
            text_align="right",
            margin_top="1em",
        ),
        rx.box(
            rx.badge(
                "assistant",
                rx.tooltip(
                    rx.icon("info", size=14), content="The current selected chat."
                ),
                variant="soft",
            ),
            rx.spacer(),
            rx.markdown(
                qa.answer,
                background_color=rx.color("accent", 4),
                color=rx.color("accent", 12),
                **message_style,
            ),
            text_align="left",
            padding_top="1em",
        ),
        width="100%",
    )


def chat() -> rx.Component:
    """List all the messages in a single conversation."""
    sidebar_width = 275

    return rx.box(
        rx.hstack(
            # Left sidebar menu (unchanged)
            rx.box(
                rx.box(
                    menu.menus_v1(),
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
            # Only change: add overflow_y="auto" to the center container
            rx.center(
                rx.vstack(
                    rx.center(
                        rx.image(src="/logo.png", width="100px", height="auto"),
                        width="100%",
                    ),
                    rx.box(
                        rx.foreach(State.chats[State.current_chat], message_exchange),
                        width="100%",
                    ),
                    py="8",
                    flex="1",
                    width="100%",
                    max_width="50em",
                    padding_x="4px",
                    align_self="center",
                    overflow="hidden",
                    padding_bottom="5em",
                ),
                background_size="20px 20px",
                background_image="radial-gradient(circle, hsl(0, 0%, 39%) 1px, transparent 1px)",  # noqa: E501
                mask="radial-gradient(50% 100% at 50% 50%, hsl(0, 0%, 0%, 1), hsl(0, 0%, 0%, 0))",  # noqa: E501
                width=f"calc(100% - {sidebar_width}px)",
                height="100vh",
                margin_left=f"{sidebar_width}px",
                # This is the only change:
                overflow_y="auto",
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
        height="100vh",
        overflow="hidden",
    )


def action_bar() -> rx.Component:
    """The action bar to send a new message."""
    return rx.center(
        rx.vstack(
            rc.form(
                input_form(),
                on_submit=State.process_question,
                reset_on_submit=True,
            ),
            align_items="center",
        ),
        position="sticky",
        bottom="0",
        left="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        align_items="stretch",
        width="100%",
    )
