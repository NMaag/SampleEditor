# Revamp Plan

This document is written as a learning guide, not just a task list.

## What We Learned From The Original Script

The existing tool already has useful business logic:

- mapping file loading
- file selection and conversion flow
- label image generation
- TIFF page inspection and comparison
- config persistence

The main challenge is structure, not capability. Right now the project mixes:

- terminal prompts
- file system configuration
- image processing logic
- output writing

That makes it harder to test, easier to break, and harder to attach a GUI.

## Revamp Strategy

### Phase 1: Create a clean repo

Goal:
Set up a modern Python project layout with room for code, tests, and docs.

Why:
This gives us a stable base before we move logic around.

### Phase 2: Extract core logic

Goal:
Move the reusable parts of the old script into importable modules.

Examples:

- `mapping.py` for CSV loading
- `labels.py` for QR/label generation
- `slides.py` for reading and writing slide files
- `config.py` for saved paths

Why:
The GUI should call functions, not re-implement behavior.

### Phase 3: Add a GUI

Goal:
Create a desktop application where users can:

- choose input/output folders
- choose a CSV mapping file
- preview files and metadata
- run single or batch conversions
- see progress and errors clearly

Recommended direction:
Use `PySide6` for the GUI because it is a strong long-term desktop toolkit and packages well on Windows.

### Phase 4: Package for sharing

Goal:
Make it easy for people to run the app without dealing with manual setup.

Likely approach:

- create an installable Python package
- add a desktop entry point
- later build a Windows executable with PyInstaller

## First Technical Refactor Targets

When we start moving code, we should preserve behavior in this order:

1. CSV loading
2. label generation
3. slide rewrite logic
4. config save/load
5. batch conversion flow

That order gives us a working core before we redesign the interface.

## Immediate Next Step

In the next step, we should copy the useful logic from the old script into new modules without changing behavior very much. That will let you learn the transition from "script" to "application architecture" in a very concrete way.

## Progress So Far

The first extraction step is now defined as:

- `src/sample_editor/core/config.py` for config persistence
- `src/sample_editor/core/mapping.py` for CSV mapping loading

These are good starter modules because they are important, small, and easy to test in isolation.
