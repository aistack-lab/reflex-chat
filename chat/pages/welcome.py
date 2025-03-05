from __future__ import annotations

import reflex as rx
import reflex_chakra as rc

from chat.template import with_template


# Import the welcome text
INTRO = """
# "🤖 Demo-Tool

## Willkommen!

Dieses Tool hilft Ihnen dabei, Informationen im Kontext des EU-AI Acts zu
analysieren und zu strukturieren.

### Workflow:
1. **Schritt 1**: Erfassen Sie die relevanten Informationen in einem
strukturierten Format
2. **Schritt 2**: Erhalten Sie eine detaillierte Analyse und können im Dialog
weitere Fragen klären

Klicken Sie auf 'Start', um zu beginnen.
"""


@rx.page(route="/")
@with_template
def welcome() -> rx.Component:
    """Welcome page showing introductory content."""
    return rc.container(
        rc.box(
            rx.markdown(INTRO),
            padding="2em",
            background_color=rx.color("mauve", 2),
            border_radius="md",
            max_width="800px",
            margin="0 auto",
            box_shadow="lg",
        ),
        rc.center(
            rx.link(
                rx.button("Start Chat", size="3", color_scheme="cyan"),
                href="/chat",
            ),
            padding_top="2em",
        ),
        padding="2em",
    )
