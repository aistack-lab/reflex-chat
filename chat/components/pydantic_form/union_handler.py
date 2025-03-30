"""Field handlers for union types (including Optional)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, get_args, get_origin

import pydantic
import reflex as rx

from .base import FieldHandler, FieldHandlerRegistry


if TYPE_CHECKING:
    from collections.abc import Callable


class UnionHandler(FieldHandler):
    """Handler for union types, including Optional[T]."""

    def __init__(self):
        """Initialize the handler."""
        self.registry = FieldHandlerRegistry()

    def supports(
        self, type_annotation: Any, field_info: pydantic.fields.FieldInfo | None = None
    ) -> bool:
        """Check if this handler supports the type."""
        return get_origin(type_annotation) is Union

    def create_widget(
        self,
        field_name: str,
        field_info: pydantic.fields.FieldInfo,
        value: Any,
        on_change: Callable[[Any], None],
        error: str | None = None,
    ) -> rx.Component:
        """Create a widget for union fields."""
        # Get the union member types
        member_types = get_args(field_info.annotation)

        # Check if this is an Optional type (Union[T, None])
        is_optional = len(member_types) == 2 and type(None) in member_types  # noqa: PLR2004

        # For Optional types, create a simpler toggle-based UI
        if is_optional:
            # Get the non-None type
            inner_type = next(t for t in member_types if t is not type(None))

            # Get a handler for the inner type
            inner_handler = None
            for handler in self.registry._handlers:
                if handler is not self and handler.supports(inner_type):
                    inner_handler = handler
                    break

            # If no handler found, return a placeholder
            if not inner_handler:
                return rx.text(f"No handler for {inner_type.__name__}")

            # Create a wrapper with a toggle for None/value
            is_present = value is not None

            # Get a default value for the inner type
            inner_default = inner_handler.get_default_value(field_info)

            # Create the widget for the inner type
            inner_widget = inner_handler.create_widget(
                field_name=field_name,
                field_info=field_info,  # Use original field_info
                value=value if is_present else inner_default,
                on_change=lambda inner_value: on_change(inner_value),
                error=error,
            )

            # Wrap with a checkbox for None toggle
            title = field_info.title or field_name.replace("_", " ").capitalize()
            return rx.vstack(
                rx.hstack(
                    rx.checkbox(
                        value=rx.Var.create(is_present),
                        on_change=lambda is_checked: on_change(
                            None if not is_checked else inner_default
                        ),
                    ),
                    rx.text(
                        f"{title} (Optional)",
                        as_="label",
                        for_=field_name,
                    ),
                    rx.badge("Optional", color_scheme="blue", variant="soft", size="1"),
                    align_items="center",
                ),
                rx.cond(
                    is_present,
                    inner_widget,
                    rx.text("None", color="gray.500", font_size="sm"),
                ),
                rx.text(error, color="red.500", font_size="sm") if error else None,
                rx.text(
                    field_info.description,
                    color="gray.500",
                    font_size="sm",
                )
                if field_info.description
                else None,
                align_items="start",
                width="100%",
                spacing="1",
            )

        # For real unions, create a dropdown + dynamic field
        # Map types to handlers and get their default values
        handlers = {}
        default_values = {}
        type_names = []

        for member_type in member_types:
            # Find a handler for this member type
            for handler in self.registry._handlers:
                if handler is not self and handler.supports(member_type):
                    type_name = getattr(member_type, "__name__", str(member_type))
                    handlers[type_name] = (handler, member_type)
                    default_values[type_name] = handler.get_default_value(field_info)
                    type_names.append(type_name)
                    break

        # If value is set, determine its type
        current_type = None
        if value is not None:
            for type_name, (_, member_type) in handlers.items():
                try:
                    # Use crude type checking
                    if isinstance(value, member_type):
                        current_type = type_name
                        break
                except TypeError:
                    # Some types can't be used with isinstance
                    pass

        # Set a default selected type if none is matched
        selected_type = current_type or (type_names[0] if type_names else None)

        # Create a dropdown to select the type
        return rx.vstack(
            rx.hstack(
                rx.text(
                    field_info.title or field_name.replace("_", " ").capitalize(),
                    as_="label",
                    for_=f"{field_name}_type",
                ),
                rx.badge("Union", color_scheme="purple", variant="soft", size="1"),
                align_items="center",
            ),
            rx.select(
                type_names,
                placeholder="Select type",
                id=f"{field_name}_type",
                value=selected_type,
                on_change=lambda type_name: on_change(default_values.get(type_name)),
                width="100%",
            ),
            rx.cond(
                selected_type is not None,
                rx.vstack(
                    # Dynamically render the field for the selected type
                    *[
                        rx.cond(
                            selected_type == type_name,
                            handler.create_widget(
                                field_name=field_name,
                                field_info=field_info,  # Use original field_info
                                value=value
                                if current_type == type_name
                                else default_values[type_name],
                                on_change=on_change,
                                error=error,
                            ),
                        )
                        for type_name, (handler, _) in handlers.items()
                    ],
                    width="100%",
                    align_items="start",
                ),
                rx.text("Select a type", color="gray.500", font_size="sm"),
            ),
            rx.text(error, color="red.500", font_size="sm") if error else None,
            rx.text(
                field_info.description,
                color="gray.500",
                font_size="sm",
            )
            if field_info.description
            else None,
            align_items="start",
            width="100%",
            spacing="1",
        )

    def get_default_value(self, field_info: pydantic.fields.FieldInfo) -> Any:
        """Get default value for a union field."""
        # First check for explicit default value
        if (
            field_info.default is not None
            and field_info.default is not pydantic.fields.PydanticUndefined
        ):
            return field_info.default

        # Check for default factory
        if field_info.default_factory is not None:
            if field_info.default_factory_takes_validated_data:
                return field_info.default_factory({})  # type: ignore
            return field_info.default_factory()  # type: ignore

        # For Optional types, return None
        member_types = get_args(field_info.annotation)
        if len(member_types) == 2 and type(None) in member_types:  # noqa: PLR2004
            return None

        # For other unions, try to find a handler for the first type
        first_type = member_types[0]
        if first_type is not type(None):
            # Find a handler for the first type
            for handler in self.registry._handlers:
                if handler is not self and handler.supports(first_type):
                    return handler.get_default_value(field_info)

        # Fallback to None
        return None


# Register the handler
registry = FieldHandlerRegistry()
registry.register(UnionHandler())
