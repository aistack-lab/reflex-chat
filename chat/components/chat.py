"""Chat components."""

from __future__ import annotations

from typing import Any

import reflex as rx
import reflex_chakra as rc

from chat.components import loading_icon, menu
from chat.components.templates import templates
from chat.state import State, UIMessage


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
                value=State.input_question,
                on_change=State.set_input_question,
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


def tool_call_component(tool_call: Any) -> rx.Component:
    """Render a tool call as a component."""
    return rx.vstack(
        rx.hstack(
            rx.icon("pen_tool", color=rx.color("cyan", 11)),
            rx.text(f"Tool: {tool_call.tool_name}", weight="bold"),
            spacing="1",
        ),
        rx.code_block(
            str(tool_call.args),
            language="json",
            theme="dark",
            copy_button=True,
            border_radius="md",
        ),
        rx.divider(),
        rx.text("Result:"),
        rx.code_block(
            # Use string representation directly to avoid conditional evaluation
            str(tool_call.result),
            language="json",
            theme="dark",
            copy_button=True,
            border_radius="md",
        ),
        padding="0.5em",
        border=f"1px solid {rx.color('cyan', 6)}",
        border_radius="md",
        width="100%",
        background_color=rx.color("cyan", 2),
    )


def message_exchange(msg: UIMessage) -> rx.Component:
    """Display a message based on its role.

    Args:
        msg: The message to display

    Returns:
        A component displaying the message
    """
    # We use conditional rendering based on a pre-set field, not computed
    return rx.box(
        rx.badge(msg.role, variant="soft"),
        rx.spacer(),
        rx.markdown(
            msg.content,
            background_color=rx.color(rx.cond(msg.role == "user", "mauve", "accent"), 4),
            color=rx.color(rx.cond(msg.role == "user", "mauve", "accent"), 12),
            **message_style,
        ),
        text_align=rx.cond(msg.role == "user", "right", "left"),
        margin_top="1em",
        width="100%",
    )


def chat() -> rx.Component:
    """List all the messages in a single conversation."""
    sidebar_width = 275

    return rx.box(
        rx.hstack(
            # Left sidebar menu
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
            # Chat content area with scrolling
            rx.box(
                rx.vstack(
                    rx.center(
                        rx.image(src="/logo.png", width="100px", height="auto"),
                        width="100%",
                    ),
                    templates(),
                    rx.box(
                        rx.foreach(State.chats[State.current_chat], message_exchange),
                        width="100%",
                        padding_bottom="80px",  # to prevent being hidden behind actionbar
                    ),
                    width="100%",
                    max_width="50em",
                    padding_x="4px",
                    align_self="center",
                    margin_x="auto",
                    spacing="4",
                ),
                background_size="20px 20px",
                background_image="radial-gradient(circle, hsl(0, 0%, 39%) 1px, transparent 1px)",  # noqa: E501
                mask="radial-gradient(50% 100% at 50% 50%, hsl(0, 0%, 0%, 1), hsl(0, 0%, 0%, 0))",  # noqa: E501
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
        width="100%",
        position="relative",
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
        position="fixed",
        bottom="0",
        left="0",
        right="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        align_items="stretch",
        width="100%",
        z_index="99",  # Ensure action bar stays on top
    )
