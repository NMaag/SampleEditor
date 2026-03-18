# SampleEditor Revamp

This repository is the new home for a friendlier version of SampleEditor.

The original project works, but most of the behavior currently lives in one terminal-driven script. The goal of this revamp is to:

- keep the slide-processing logic that already works
- separate core logic from user interface code
- add a desktop GUI so users do not need to work in a terminal
- make packaging and sharing easier

## Current Direction

We are rebuilding the project in stages so the behavior stays understandable:

1. document what the original tool does
2. create a clean Python package layout
3. move reusable logic into `src/sample_editor/core/`
4. build a GUI on top of that logic
5. package the app for easier distribution

## Proposed Layout

```text
src/sample_editor/
  app.py
  core/
  gui/
tests/
docs/
```

## Current CLI Usage

Once dependencies are installed, you can run the in-progress command-line app with:

```powershell
py -3.14 -m pip install -e .
py -3.14 -m sample_editor
```

This is still a transitional interface, but it now gives us a real command entry point while we build the GUI.

## Original Project Notes

The original project in `C:\Users\zh0703\Downloads\SampleEditor 1\SampleEditor` currently:

- loads a CSV mapping between `HE Image ID` and `Block ID`
- reads `.svs` files with `tifffile`
- replaces the label page with a generated QR-code label
- writes a new output file
- supports single convert, batch convert, compare, view, and path configuration

*One important cleanup item is that the main script is currently saved as `SampleEditor.txt`, even though it contains Python code. In the new repo we will use normal `.py` files and split responsibilities into modules.
