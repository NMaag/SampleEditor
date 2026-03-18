"""GUI application entry point for SampleEditor."""

from __future__ import annotations

import sys


def main() -> None:
    """Launch the GUI application."""
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:
        raise SystemExit(
            "PySide6 is not installed. Run `py -3.14 -m pip install -e .[gui]` first."
        ) from exc

    from sample_editor.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
