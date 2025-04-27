"""Session state."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import Any, Literal
import uuid

from llmling_agent import ChatMessage, ToolCallInfo  # noqa: TC002
from llmling_agent.messaging.messages import TokenCost  # noqa: TC002
from pydantic import BaseModel, Field
import reflex as rx
import reflexions as rfx

from chat.agents import pool


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

    chats: rx.Field[dict[str, list[UIMessage]]] = rx.field(DEFAULT_CHATS)
    current_chat = "Intros"
    processing: bool = False
    new_chat_name: str = ""
    input_question: str = ""

    def create_chat(self):
        """Create a new chat."""
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = next(iter(self.chats.keys()))

    async def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name

    @rx.event
    def set_input_question(self, value: str | rfx.CardItem) -> None:
        """Update the current input question.

        Args:
            value: The new input question value
        """
        match value:
            case rfx.CardItem():
                self.input_question = value.description
            case dict():
                self.input_question = value.get("description", "")
            case _:
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

        messages = self.chats[self.current_chat]
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                # Regular case: we have both user and assistant messages
                user_content = messages[i].content
                assistant_content = messages[i + 1].content
                result.append([user_content, assistant_content])
            else:
                # Edge case: only user message exists
                user_content = messages[i].content
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

        user_message = UIMessage(role="user", content=question)
        self.chats[self.current_chat].append(user_message)
        assistant_message = UIMessage(role="assistant", content="")
        self.chats[self.current_chat].append(assistant_message)
        self.processing = True
        yield
        messages = []
        for msg in self.chats[self.current_chat][:-1]:  # Exclude empty assistant message
            chat_message = ChatMessage(content=msg.content, role=msg.role)
            messages.append(chat_message)
        agent = pool.get_agent("simple_agent")
        async with agent.run_stream(question) as stream:
            # Stream the results
            async for chunk in stream.stream():
                assistant_msg_idx = len(self.chats[self.current_chat]) - 1
                self.chats[self.current_chat][assistant_msg_idx].content = chunk
                yield
        # Update with final result and metadata
        if result := agent.conversation.chat_messages[-1]:
            # Convert the full ChatMessage result to our UIMessage format
            ui_message = UIMessage.from_chat_message(result)
            # Update our assistant message with all the metadata
            assistant_msg_idx = len(self.chats[self.current_chat]) - 1
            self.chats[self.current_chat][assistant_msg_idx] = ui_message

        self.processing = False
