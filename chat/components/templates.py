from __future__ import annotations

import reflex as rx

from chat.state import State


# https://github.com/reflex-dev/reflex-llamaindex-template/blob/main/frontend/views/templates.py


def template_card(icon: str, title: str, description: str, color: str) -> rx.Component:
    return rx.el.button(
        rx.icon(tag=icon, color=rx.color(color, 9), size=16),
        rx.text(title, class_name="font-medium text-slate-11 text-sm"),
        rx.text(description, class_name="text-slate-10 text-xs"),
        class_name="relative align-top flex flex-col gap-2 border-slate-4 bg-slate-1 hover:bg-slate-3 shadow-sm px-3 pt-3 pb-4 border rounded-2xl text-[15px] text-start transition-colors",  # noqa: E501
        on_click=[State.set_input_question(description)],  # type: ignore
    )


def templates() -> rx.Component:
    return rx.box(
        rx.box(
            template_card(
                "message-circle",
                "Erstelle ein Ticket",
                "Erstelle ein Jira-Ticket mit Priorität 'high' mit dem Titel 'ABC'",
                "grass",
            ),
            template_card(
                "calculator",
                "Suche nach Tickets",
                "Welche Tickets mit Priorität 'Medium' sind im System?",
                "tomato",
            ),
            template_card(
                "globe",
                "Web-Suche",
                "Suche nach Informationen über Jira Query language.",
                "blue",
            ),
            template_card(
                "book",
                "Dokumente durchsuchen",
                "Was steht in der Datei XY?",
                "amber",
            ),
            class_name="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 w-full",
        ),
        class_name="top-1/3 left-1/2 absolute flex flex-col justify-center items-center gap-10 w-full max-w-4xl transform -translate-x-1/2 -translate-y-1/2 px-6 z-50",  # noqa: E501
        style={
            "animation": "reveal 0.35s ease-out",
            "@keyframes reveal": {"0%": {"opacity": "0"}, "100%": {"opacity": "1"}},
        },
        # Use a computed var or another approach to conditionally display
        display="flex",
    )
