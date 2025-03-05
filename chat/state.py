"""Session state."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
import os
from typing import Any, Literal
import uuid

from llmling_agent import ChatMessage, ToolCallInfo  # noqa: TC002
from llmling_agent.messaging.messages import TokenCost  # noqa: TC002
from pydantic import BaseModel, Field
import reflex as rx

from chat.agents import pool


# Checking if the API key is set properly
if not os.getenv("OPENAI_API_KEY"):
    msg = "Please set OPENAI_API_KEY environment variable."
    raise Exception(msg)  # noqa: TRY002


class UIMessage(BaseModel):
    """A serializable message for the UI with pre-formatted display fields."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    model: str | None = None
    timestamp: datetime | None = None
    cost_info: TokenCost | None = None
    response_time: float | None = None
    tool_calls: list[ToolCallInfo] = Field(default_factory=list)
    name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_chat_message(cls, message: ChatMessage) -> UIMessage:
        """Convert a ChatMessage to a UIMessage."""
        return cls(
            id=message.message_id,
            role=message.role,
            content=str(message.content),
            model=message.model,
            timestamp=message.timestamp,
            cost_info=message.cost_info,
            response_time=message.response_time,
            tool_calls=message.tool_calls,
            name=message.name,
            metadata=message.metadata,
        )


DEFAULT_CHATS: dict[str, list[UIMessage]] = {"Intros": []}


class State(rx.State):
    """The app state."""

    chats: dict[str, list[UIMessage]] = DEFAULT_CHATS
    current_chat_name = "Intros"
    processing: bool = False
    new_chat_name: str = ""
    input_question: str = ""

    def create_chat(self):
        """Create a new chat."""
        self.current_chat_name = self.new_chat_name
        self.chats[self.new_chat_name] = []

    @rx.var(cache=True)
    def current_chat(self) -> list[UIMessage]:
        """Get the UI Messages of current chat.

        Returns:
            The list of UIMessages of the current chat.
        """
        return self.chats[self.current_chat_name]

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat_name]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat_name = next(iter(self.chats.keys()))

    async def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat_name = chat_name

    def set_input_question(self, value: str) -> None:
        """Update the current input question.

        Args:
            value: The new input question value
        """
        self.input_question = value

    @rx.var(cache=True)
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    def format_chat_history(self) -> list:
        """Format the chat history into pairs of [user_content, assistant_content]."""
        result = []

        for i in range(0, len(self.current_chat), 2):
            if i + 1 < len(self.current_chat):
                # Regular case: we have both user and assistant messages
                user_content = self.current_chat[i].content
                assistant_content = self.current_chat[i + 1].content
                result.append([user_content, assistant_content])
            else:
                # Edge case: only user message exists
                user_content = self.current_chat[i].content
                result.append([user_content, ""])

        return result

    async def process_question(self, form_data: dict[str, Any]):
        """Process a question from the form.

        Args:
            form_data: Form data containing the question.
        """
        question = form_data["question"]
        if question == "":
            return
        self.input_question = ""
        async for value in self.openai_process_question(question):
            yield value

    async def openai_process_question(self, question: str):
        """Get the response from the API.

        Args:
            question: The current question.
        """
        from llmling_agent import ChatMessage

        # Create a user message
        user_message = UIMessage(role="user", content=question)
        self.current_chat.append(user_message)

        # Create an empty assistant message
        assistant_message = UIMessage(role="assistant", content="")
        self.current_chat.append(assistant_message)

        # Start processing
        self.processing = True
        yield

        # Build chat history
        messages = []
        for msg in self.current_chat[:-1]:  # Exclude empty assistant message
            chat_message = ChatMessage(content=msg.content, role=msg.role)
            messages.append(chat_message)

        # Process with agent
        agent = pool.get_agent("simple_agent")
        async with agent.run_stream(question) as stream:
            async for chunk in stream.stream():
                assistant_msg_idx = len(self.current_chat) - 1
                self.current_chat[assistant_msg_idx].content = chunk
                yield
        # Update with final result and metadata
        if result := agent.conversation.chat_messages[-1]:
            # Convert the full ChatMessage result to our UIMessage format
            ui_message = UIMessage.from_chat_message(result)
            # Update our assistant message with all the metadata
            assistant_msg_idx = len(self.current_chat) - 1
            self.current_chat[assistant_msg_idx] = ui_message

        self.processing = False
