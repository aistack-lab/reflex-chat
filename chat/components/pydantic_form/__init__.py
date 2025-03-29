"""Pydantic form component for automatic form generation from Pydantic models."""

from __future__ import annotations

from .base import FieldHandler, FieldHandlerRegistry, pydantic_form

__all__ = ["FieldHandler", "FieldHandlerRegistry", "pydantic_form"]
