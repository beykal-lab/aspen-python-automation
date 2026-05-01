"""Thin COM adapter for Aspen Plus automation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class AspenComAdapter:
    """Wrap pywin32 calls so executor logic stays testable."""

    def __init__(self, visible: bool = True) -> None:
        self.visible = visible
        self.app: Any | None = None

    def start(self) -> str:
        import win32com.client as win32  # type: ignore[import-not-found]

        if self.app is None:
            self.app = win32.Dispatch("Apwn.Document")
        return "Aspen COM dispatch succeeded."

    def open_archive(self, path: Path) -> str:
        self._require_app().InitFromArchive2(str(path.resolve()))
        self._try_set_visible()
        return f"opened archive: {path}"

    def open_input_file(self, path: Path) -> str:
        self._require_app().InitFromFile2(str(path.resolve()), False)
        self._try_set_visible()
        return f"imported input file: {path}"

    def run(self) -> str:
        self._require_app().Run2(False)
        return "Aspen run completed."

    def write_archive(self, path: Path) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._require_app().WriteArchive2(str(path.resolve()), True)
        return f"wrote archive: {path}"

    def read_node(self, path: str) -> object:
        node = self._require_app().Tree.FindNode(path)
        return node.Value

    def close(self) -> None:
        if self.app is None:
            return
        try:
            self.app.Close(False)
        finally:
            self.app = None

    def _require_app(self) -> Any:
        if self.app is None:
            self.start()
        return self.app

    def _try_set_visible(self) -> None:
        if not self.visible:
            return
        try:
            self._require_app().Visible = True
        except Exception:
            pass
