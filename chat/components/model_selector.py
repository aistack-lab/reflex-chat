"""Model selector component for Reflex applications."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import reflex as rx
import reflex_chakra as rc


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tokonomics.model_discovery import ProviderType


class ModelSelectorState(rx.State):
    """State for the model selector component."""

    models: list[Any] = []
    available_providers: list[str] = []
    provider_models: list[Any] = []
    model_names: list[str] = []
    selected_provider: str = ""
    selected_model_name: str = ""
    selected_model: Any = None
    is_expanded: bool = True
    current_model_id: str = ""

    def initialize(self, agent, providers: Sequence[ProviderType] | None = None) -> None:
        """Initialize the model selector state.

        Args:
            agent: The agent to use for model selection
            providers: Optional list of providers to filter by
        """
        from tokonomics.model_discovery import get_all_models_sync

        self.models = get_all_models_sync(providers=providers)
        self.available_providers = sorted({model.provider for model in self.models})
        self.current_model_id = agent.model_name

        current_model = None
        current_provider = None

        if self.current_model_id:
            current_model = next(
                (m for m in self.models if m.pydantic_ai_id == self.current_model_id),
                None,
            )
            if current_model:
                current_provider = current_model.provider

        # Set initial provider
        if len(self.available_providers) > 0:
            if current_provider in self.available_providers:
                self.selected_provider = current_provider
            else:
                self.selected_provider = self.available_providers[0]

            self._update_provider_models()

        # Set initial model
        if current_model and current_model.provider == self.selected_provider:
            self.selected_model_name = current_model.name
            self.selected_model = current_model

    def on_provider_change(self, provider: str) -> None:
        """Handle provider change.

        Args:
            provider: The selected provider
        """
        self.selected_provider = provider
        self._update_provider_models()

        # Select first model of new provider
        if self.model_names:
            self.selected_model_name = self.model_names[0]
            self._update_selected_model()

    def on_model_change(self, model_name: str) -> None:
        """Handle model change.

        Args:
            model_name: The selected model name
        """
        self.selected_model_name = model_name
        self._update_selected_model()

    def toggle_expanded(self) -> None:
        """Toggle expanded state."""
        self.is_expanded = not self.is_expanded

    def _update_provider_models(self) -> None:
        """Update models based on selected provider."""
        self.provider_models = [
            m for m in self.models if m.provider == self.selected_provider
        ]
        self.model_names = [m.name for m in self.provider_models]

    def _update_selected_model(self) -> None:
        """Update selected model based on selected name."""
        self.selected_model = next(
            (m for m in self.provider_models if m.name == self.selected_model_name),
            None,
        )


def model_selector(
    *,
    agent: Any,
    providers: Sequence[str] | None = None,
    expanded: bool = True,
    on_model_change: Callable[[Any], None] | None = None,
) -> rx.Component:
    """Render a model selector with provider and model dropdowns.

    This component uses the agent's current model configuration and
    provides UI to select models.

    Args:
        agent: Agent object with set_model method and model_name attribute
        providers: List of providers to show models from
        expanded: Whether to expand the model details by default
        on_model_change: Optional callback when model changes

    Returns:
        Reflex component for model selection
    """
    # Initialize state on first render
    rx.call_script(ModelSelectorState.initialize, agent, providers)

    # Build the component
    return rx.vstack(
        rx.heading("Model Selection", size="md", mb="2"),
        # Provider selector (only shown when multiple providers available)
        rx.cond(
            len(ModelSelectorState.available_providers) > 1,
            rc.form_control(
                rc.form_label("Provider"),
                rx.select(
                    ModelSelectorState.available_providers,
                    value=ModelSelectorState.selected_provider,
                    on_change=ModelSelectorState.on_provider_change,
                    placeholder="Select provider",
                ),
                mb="4",
            ),
        ),
        # Model selector
        rx.cond(
            len(ModelSelectorState.model_names) > 0,
            rc.form_control(
                rc.form_label("Model"),
                rx.select(
                    ModelSelectorState.model_names,
                    value=ModelSelectorState.selected_model_name,
                    on_change=ModelSelectorState.on_model_change,
                    placeholder="Select model",
                ),
                mb="4",
            ),
        ),
        # Model details expander
        rx.cond(
            ModelSelectorState.selected_model is not None,
            rx.vstack(
                rx.hstack(
                    rx.heading("Model Details", size="sm"),
                    rx.spacer(),
                    rx.button(
                        rx.cond(
                            ModelSelectorState.is_expanded,
                            rx.icon(tag="chevron-up"),
                            rx.icon(tag="chevron-down"),
                        ),
                        variant="ghost",
                        size="sm",
                        on_click=ModelSelectorState.toggle_expanded,
                    ),
                    width="100%",
                ),
                rx.cond(
                    ModelSelectorState.is_expanded,
                    rx.box(
                        rx.markdown(ModelSelectorState.selected_model.format()),
                        background_color=rx.color("mauve", 2),
                        padding="3",
                        border_radius="md",
                    ),
                ),
                border="1px solid",
                border_color=rx.color("mauve", 4),
                border_radius="md",
                padding="3",
                width="100%",
            ),
        ),
        width="100%",
        align_items="stretch",
        spacing="4",
    )
