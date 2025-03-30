"""Base classes and main logic for Pydantic form generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
from pydantic import BaseModel
import reflex as rx


if TYPE_CHECKING:
    from collections.abc import Callable


T = TypeVar("T", bound=BaseModel)


class FieldHandler:
    """Base handler for processing Pydantic model fields."""

    def supports(
        self, type_annotation: Any, field_info: pydantic.fields.FieldInfo | None = None
    ) -> bool:
        """Determine if this handler can process the given field.

        Args:
            type_annotation: Type annotation of the field
            field_info: Pydantic field info object

        Returns:
            True if this handler can process the field, False otherwise
        """
        raise NotImplementedError

    def create_widget(
        self,
        field_name: str,
        field_info: pydantic.fields.FieldInfo,
        value: Any,
        on_change: Callable[[Any], None],
        error: str | None = None,
    ) -> rx.Component:
        """Create a form widget for the field.

        Args:
            field_name: Name of the field
            field_info: Pydantic field info object
            value: Current field value
            on_change: Callback for when value changes
            error: Optional error message to display

        Returns:
            A Reflex component for the field
        """
        raise NotImplementedError

    def get_default_value(self, field_info: pydantic.fields.FieldInfo) -> Any:
        """Get a default value for the field if none is provided.

        Args:
            field_info: Pydantic field info object

        Returns:
            A suitable default value for the field
        """
        raise NotImplementedError


class FieldHandlerRegistry:
    """Registry of field handlers."""

    def __init__(self):
        """Initialize an empty registry."""
        self._handlers: list[FieldHandler] = []

    def register(self, handler: FieldHandler) -> None:
        """Register a field handler."""
        self._handlers.append(handler)

    def get_handler_for_field(
        self, field_info: pydantic.fields.FieldInfo
    ) -> FieldHandler | None:
        """Get the appropriate handler for a field."""
        for handler in self._handlers:
            if handler.supports(field_info.annotation, field_info):
                return handler
        return None

    def get_handler_for_type(self, type_annotation: Any) -> FieldHandler | None:
        """Get the appropriate handler for a type annotation."""
        for handler in self._handlers:
            if handler.supports(type_annotation):
                return handler
        return None


class PydanticFormState(rx.State):
    """State for the Pydantic form component."""

    model: BaseModel | None = None
    errors: dict[str, str] = {}  # noqa: RUF012
    submitting: bool = False
    submitted: bool = False
    _on_submit_callback: Callable[[BaseModel], None] | None = None

    def init_state(self):
        """Initialize state."""
        self.model = None
        self.errors = {}
        self.submitting = False
        self.submitted = False
        self._on_submit_callback = None

    def initialize(self, model_or_class: type[BaseModel] | BaseModel) -> None:
        """Initialize form state with a model.

        Args:
            model_or_class: Pydantic model class or instance
        """
        # If given a class, create an instance with defaults
        if isinstance(model_or_class, type):
            self.model = self._create_default_instance(model_or_class)
        else:
            # Use the instance directly
            self.model = model_or_class

    @rx.event
    def set_callback(self, callback: Callable[[BaseModel], None]) -> None:
        """Set the submission callback."""
        self._on_submit_callback = callback

    @rx.event
    def handle_submit(self):
        """Handle form submission."""
        self.submitting = True

        if self.validate_form() and self.model and self._on_submit_callback:
            # Form is valid
            self.submitted = True
            self._on_submit_callback(self.model)

        self.submitting = False

    @rx.event
    def update_field(self, field_name: str, value: Any) -> None:
        """Update a single field in the model.

        Args:
            field_name: Name of the field to update
            value: New value for the field
        """
        if self.model:
            # Update the model field directly
            setattr(self.model, field_name, value)

            # Clear any previous error for this field
            if field_name in self.errors:
                self.errors.pop(field_name)

    def validate_form(self) -> bool:
        """Validate the entire model.

        Returns:
            True if validation succeeded, False otherwise
        """
        if not self.model:
            return False

        try:
            self.model.__class__.model_validate(self.model.model_dump())
            self.errors = {}
        except pydantic.ValidationError as e:
            # Convert validation errors to field-specific error messages
            self.errors = {
                err["loc"][0]: err["msg"]
                for err in e.errors()
                if isinstance(err["loc"], tuple) and len(err["loc"]) > 0
            }
            return False
        else:
            return True

    def _create_default_instance(self, model_class: type[BaseModel]) -> BaseModel:
        """Create a default instance of a model.

        Args:
            model_class: Pydantic model class

        Returns:
            Default instance of the model
        """
        registry = FieldHandlerRegistry()
        default_values = {}
        for field_name, field in model_class.model_fields.items():
            handler = registry.get_handler_for_field(field)

            if handler:
                default_values[field_name] = handler.get_default_value(field)
            elif field.default is not pydantic.fields.PydanticUndefined:
                default_values[field_name] = field.default
            elif field.default_factory is not None:
                # Use field's default factory
                if field.default_factory_takes_validated_data:
                    default_values[field_name] = field.default_factory({})  # type: ignore
                else:
                    default_values[field_name] = field.default_factory()  # type: ignore

        try:
            return model_class.model_validate(default_values)
        except pydantic.ValidationError:
            # Fallback to empty model if validation fails
            return model_class.model_construct()


def pydantic_form(
    model: type[T] | T,
    *,
    on_submit: Callable[[T], None] | None = None,
    exclude_fields: list[str] | None = None,
    include_fields: list[str] | None = None,
    field_overrides: dict[str, dict[str, Any]] | None = None,
    disable_validation: bool = False,
    layout: str = "vertical",
    submit_label: str = "Submit",
) -> rx.Component:
    """Generate a form from a Pydantic model.

    Args:
        model: Pydantic model class or instance
        on_submit: Callback function when form is submitted with valid data
        exclude_fields: Optional list of field names to exclude from the form
        include_fields: Optional list of field names to include
        field_overrides: Optional customizations for specific fields
        disable_validation: Whether to disable client-side validation
        layout: Form layout style ("vertical", "horizontal", "compact")
        submit_label: Text to display on the submit button

    Returns:
        A Reflex component representing the form
    """
    # Initialize form state
    form_state = PydanticFormState()
    rx.script(form_state.initialize, model)

    # Set the callback if provided
    if on_submit:
        rx.script(form_state.set_callback, on_submit)

    model_class = model if isinstance(model, type) else model.__class__
    fields_to_show = []
    if include_fields:
        fields_to_show = include_fields
    else:
        fields_to_show = list(model_class.model_fields.keys())
        if exclude_fields:
            fields_to_show = [f for f in fields_to_show if f not in exclude_fields]

    form_fields = []
    registry = FieldHandlerRegistry()

    for field_name in fields_to_show:
        if field_name not in model_class.model_fields:
            continue

        field_info = model_class.model_fields[field_name]
        handler = registry.get_handler_for_field(field_info)

        if not handler:
            # Skip fields without handlers
            continue

        field_widget = handler.create_widget(
            field_name=field_name,
            field_info=field_info,
            value=getattr(form_state.model, field_name, None)
            if form_state.model
            else None,
            on_change=lambda value, name=field_name: form_state.update_field(name, value),
            error=form_state.errors.get(field_name),
        )

        form_fields.append(field_widget)

    return rx.vstack(
        *form_fields,
        rx.hstack(
            rx.spacer(),
            rx.button(
                submit_label,
                type="submit",
                is_disabled=form_state.submitting,
                on_click=form_state.handle_submit,
            ),
            width="100%",
        ),
        width="100%",
        align_items="stretch",
        spacing="4",
    )
