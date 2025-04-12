from __future__ import annotations

from typing import TYPE_CHECKING

import reflexions as rfx

from chat.state import State


if TYPE_CHECKING:
    import reflex as rx


item_1 = rfx.CardItem(
    icon="message-circle",
    title="Erstelle ein Ticket",
    description="Erstelle ein Jira-Ticket mit Priorität 'high' mit dem Titel 'ABC'",
    color="grass",
)

item_2 = rfx.CardItem(
    icon="calculator",
    title="Suche nach Tickets",
    description="Welche Tickets mit Priorität 'Medium' sind im System?",
    color="tomato",
)

item_3 = rfx.CardItem(
    icon="globe",
    title="Web-Suche",
    description="Suche nach Informationen über Jira Query language.",
    color="blue",
)

item_4 = rfx.CardItem(
    icon="book",
    title="Dokumente durchsuchen",
    description="Was steht in der Datei XY?",
    color="amber",
)


def templates() -> rx.Component:
    return rfx.cards([item_1, item_2, item_3, item_4], on_click=State.set_input_question)
