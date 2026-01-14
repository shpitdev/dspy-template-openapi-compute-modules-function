"""Shared typing helpers."""

from __future__ import annotations

from enum import StrEnum


class ClassificationType(StrEnum):
    AE_PC = "ae-pc"
    AE_CATEGORY = "ae-category"
    PC_CATEGORY = "pc-category"


__all__ = ["ClassificationType"]
