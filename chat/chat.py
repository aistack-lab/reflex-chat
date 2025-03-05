"""The main Chat app."""

from __future__ import annotations

from contextlib import asynccontextmanager

import reflex as rx

from chat.agents import pool
from chat.pages import chat_page, welcome


# Add state and page to the app.
theme = rx.theme(appearance="dark", accent_color="cyan", scaling="110%", radius="small")
app = rx.App(theme=theme)


@asynccontextmanager
async def run_pool():
    async with pool:
        yield


app.register_lifespan_task(run_pool)

# Register the pages
app.add_page(welcome)
app.add_page(chat_page)
