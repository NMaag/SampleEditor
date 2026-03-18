"""Deprecated terminal entry point kept only as a compatibility stub."""

from __future__ import annotations


def main() -> None:
    """Tell users to launch the GUI instead of the old terminal workflow."""
    raise SystemExit(
        "Terminal mode has been retired. Run `py -3.14 -m sample_editor` to use the GUI."
    )


if __name__ == "__main__":
    main()
