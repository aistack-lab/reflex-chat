"""Session state."""

from __future__ import annotations

import os
from typing import Any

from llmling_agent import Agent, ChatMessage
import reflex as rx


# Checking if the API key is set properly
if not os.getenv("OPENAI_API_KEY"):
    msg = "Please set OPENAI_API_KEY environment variable."
    raise Exception(msg)  # noqa: TRY002


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


DEFAULT_CHATS: dict[str, list[Any]] = {"Intros": []}


class State(rx.State):
    """The app state."""

    chats: dict[str, list[QA]] = DEFAULT_CHATS  # chat name -> questions / answers.
    current_chat = "Intros"  # The current chat name.
    question: str  # The current question.
    processing: bool = False  # Whether we are processing the question.
    new_chat_name: str = ""  # The name of the new chat.

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = next(iter(self.chats.keys()))

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name

    @rx.var(cache=True)
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    async def process_question(self, form_data: dict[str, Any]):
        question = form_data["question"]  # Get the question from the form
        if question == "":  # Check if the question is empty
            return
        async for value in self.openai_process_question(question):
            yield value

    async def openai_process_question(self, question: str):
        """Get the response from the API.

        Args:
            question: The current question.
        """
        # Add the question to the list of questions.
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        yield

        # Build the messages.
        messages: list[ChatMessage] = []
        for qa in self.chats[self.current_chat]:
            messages.append(ChatMessage(qa.question, role="user"))
            messages.append(ChatMessage(qa.answer, role="assistant"))

        # Remove the last mock answer.
        messages = messages[:-1]
        agent = Agent[None](
            model="openai:gpt-4o-mini",
            system_prompt="You are a friendly chatbot named Reflex. Respond in markdown.",
        )
        async with agent.run_stream(question) as stream:
            # Stream the results, yielding after every word.
            async for chunk in stream.stream():
                self.chats[self.current_chat][-1].answer = chunk
                self.chats = self.chats
                yield

            # Toggle the processing flag.
            self.processing = False
