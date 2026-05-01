"""Aspen availability checks and connection status models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AspenStatus:
    mode: str
    available: bool
    message: str


class AspenConnection:
    """Check Aspen availability without forcing COM import during normal CLI use."""

    def __init__(self, mode: str = "detect") -> None:
        if mode not in {"dry-run", "detect", "execute"}:
            raise ValueError("mode must be one of: dry-run, detect, execute")
        self.mode = mode

    def check(self) -> AspenStatus:
        if self.mode == "dry-run":
            return AspenStatus(
                mode=self.mode,
                available=True,
                message="dry-run mode: Aspen COM is not required.",
            )

        try:
            import win32com.client as win32  # type: ignore[import-not-found]
        except Exception as exc:
            return AspenStatus(
                mode=self.mode,
                available=False,
                message=f"Aspen COM is unavailable: {type(exc).__name__}: {exc}",
            )

        if self.mode == "detect":
            return AspenStatus(
                mode=self.mode,
                available=True,
                message="pywin32 is available; Aspen dispatch was not started in detect mode.",
            )

        try:
            win32.Dispatch("Apwn.Document")
        except Exception as exc:
            return AspenStatus(
                mode=self.mode,
                available=False,
                message=f"Aspen dispatch failed: {type(exc).__name__}: {exc}",
            )

        return AspenStatus(
            mode=self.mode,
            available=True,
            message="Aspen dispatch succeeded.",
        )
